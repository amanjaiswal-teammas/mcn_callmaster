import time
import mysql.connector
import logging
import os
import json
import re
from datetime import datetime
from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------- CONFIG ----------
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

# ---------- DB ----------
DIALER_DB = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "dialer_db",
    "connection_timeout": 10,
    "autocommit": True
}

AUDIT_DB = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "db_external",
    "connection_timeout": 10,
    "autocommit": True
}

PROMPT_DB = {
    "host": "192.168.11.6",
    "user": "root",
    "password": "dial@mas123",
    "database": "db_dialdesk"
}

# ---------- HELPERS ----------

def deepgram_transcribe(audio_url: str) -> str:
    try:
        if not audio_url:
            return ""

        session = requests.Session()

        headers_req = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
            "Referer": "http://192.168.10.9/",
            "Connection": "keep-alive"
        }

        def fetch(url):
            return session.get(
                url,
                headers=headers_req,
                timeout=60,
                verify=False   # 🔥 SSL safety
            )

        audio_res = None

        # 🔁 RETRY LOOP
        for attempt in range(3):
            try:
                audio_res = fetch(audio_url)

                # 🔴 HANDLE 403
                if audio_res.status_code == 403:
                    alt_url = audio_url.replace("/MP3/", "/").replace(".mp3", ".wav")
                    logging.warning(f"[Attempt {attempt+1}] 403 → WAV fallback: {alt_url}")
                    audio_res = fetch(alt_url)

                # 🔴 HANDLE 404
                if audio_res.status_code == 404:
                    match = re.search(r"(192\.168\.\d+\.\d+)", audio_url)
                    if match:
                        ip = match.group(1)
                        ip_underscore = ip.replace(".", "_")

                        filename = audio_url.split("/")[-1]

                        date_match = re.search(r"_(\d{8})-", filename)
                        date_part = date_match.group(1) if date_match else datetime.now().strftime("%Y%m%d")

                        proxy_url = f"http://192.168.11.251/{ip_underscore}/{date_part}/{filename}"

                        logging.warning(f"[Attempt {attempt+1}] 404 → proxy: {proxy_url}")
                        audio_res = fetch(proxy_url)

                # ✅ SUCCESS
                if audio_res.status_code == 200:
                    break

                logging.warning(f"[Attempt {attempt+1}] Failed: {audio_res.status_code}")
                time.sleep(2)

            except Exception as e:
                logging.warning(f"[Attempt {attempt+1}] Error: {e}")
                time.sleep(2)

        else:
            logging.error(f"Audio fetch failed after retries: {audio_url}")
            return ""

        audio_bytes = audio_res.content

        if not audio_bytes:
            logging.error(f"Empty audio file: {audio_url}")
            return ""

        # 🎧 Detect content type
        content_type = "audio/mpeg"
        if audio_url.lower().endswith(".wav"):
            content_type = "audio/wav"

        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": content_type
        }

        params = {
            "punctuate": "true",
            "model": "nova"
        }

        res = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers=headers,
            params=params,
            data=audio_bytes,
            timeout=180
        )

        if res.status_code != 200:
            logging.error(f"Deepgram failed: {res.text}")
            return ""

        return (
            res.json()
            .get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
            .get("transcript", "")
        ).strip()

    except Exception as e:
        logging.error(f"Deepgram error: {e}")
        return ""


def send_to_gpt(prompt: str) -> dict:
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = res.choices[0].message.content
        match = re.search(r"\{[\s\S]*\}", content)
        return json.loads(match.group(0)) if match else {}

    except Exception as e:
        logging.error(f"GPT error: {e}")
        return {}


def get_prompt(client_id):
    conn = mysql.connector.connect(**PROMPT_DB)
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT Prompt
        FROM tbl_prompt_ob
        WHERE ClientId=%s AND status=1
        ORDER BY id DESC LIMIT 1
    """, (client_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row["Prompt"] if row else ""


def safe_epoch(dt):
    try:
        return int(dt.timestamp()) if dt else 0
    except:
        return 0


def get_connection(db_config):
    return mysql.connector.connect(**db_config)


# ---------- WORKER ----------

def worker_loop():

    while True:
        dialer_conn = None
        dialer_cur = None
        audit_conn = None
        audit_cur = None

        try:
            dialer_conn = get_connection(DIALER_DB)
            dialer_cur = dialer_conn.cursor(dictionary=True)

            dialer_conn.ping(reconnect=True, attempts=3, delay=2)

            # 🔥 fetch outbound call
            dialer_cur.execute("""
                SELECT *
                FROM call_logs
                WHERE flag = 0
                AND call_type = 'outbound'
                ORDER BY id ASC
                LIMIT 1
            """)

            row = dialer_cur.fetchone()

            # 🔥 CLOSE CONNECTION BEFORE API CALLS
            dialer_cur.close()
            dialer_conn.close()

            if not row:
                logging.info("No outbound calls...")
                time.sleep(10)
                continue

            # ⏱ Skip fresh calls (CRITICAL FIX)
            age_seconds = (datetime.now() - row["start_time"]).total_seconds()

            if age_seconds < 900:  # 15 minutes
                logging.info(f"⏳ Skipping fresh call {row['id']} ({int(age_seconds)}s old)")
                time.sleep(2)
                continue

            client_id = row["client_id"]

            prompt = get_prompt(client_id)
            if not prompt:
                logging.warning(f"No prompt for {client_id}")

                dialer_conn = get_connection(DIALER_DB)
                dialer_cur = dialer_conn.cursor()

                dialer_cur.execute("UPDATE call_logs SET flag=3 WHERE id=%s", (row["id"],))
                continue

            transcription = deepgram_transcribe(row["recording_path"])

            start_epoch = safe_epoch(row["start_time"])
            end_epoch = safe_epoch(row["end_time"])
            duration = row["duration"]

            audit_conn = get_connection(AUDIT_DB)
            audit_cur = audit_conn.cursor()

            if not transcription:
                logging.warning(f"No transcription for {row['id']}")

                audit_cur.execute("""
                                INSERT INTO CallDetails (
                                    client_id, length_in_sec,
                                    start_epoch, end_epoch, CallDate,
                                    AgentName, MobileNo, TranscribeText, entrydate
                                )
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """, (
                    client_id,
                    duration,
                    start_epoch,
                    end_epoch,
                    row["start_time"],
                    row["agent_id"],
                    row["lead_id"],
                    "",
                    datetime.now()
                ))

                audit_conn.commit()

                dialer_conn = get_connection(DIALER_DB)
                dialer_cur = dialer_conn.cursor()

                dialer_cur.execute(
                    "UPDATE call_logs SET flag=2 WHERE id=%s",
                    (row["id"],)
                )
                continue

            gpt_data = send_to_gpt(
                f"{prompt}\n\nConversation:\n{transcription}"
            )

            # ---------- INSERT ----------

            insert_data = {
                "client_id": client_id,
                "length_in_sec": duration,
                "start_epoch": start_epoch,
                "end_epoch": end_epoch,
                "CallDate": row["start_time"],
                "AgentName": row["agent_id"],
                "MobileNo": row["lead_id"],

                "CallDisposition": None,

                "Opening": gpt_data.get("Opening"),
                "Offered": gpt_data.get("Offered"),
                "ObjectionHandling": gpt_data.get("ObjectionHandling"),
                "PrepaidPitch": gpt_data.get("PrepaidPitch"),
                "UpsellingEfforts": gpt_data.get("UpsellingEfforts"),
                "OfferUrgency": gpt_data.get("OfferUrgency"),

                "SensitiveWordUsed": gpt_data.get("SensitiveWordUsed"),
                "SensitiveWordContext": gpt_data.get("SensitiveWordContext"),

                "AreaForImprovement": gpt_data.get("AreaForImprovement"),
                "TranscribeText": transcription,

                "OpeningRejected": gpt_data.get("OpeningRejected"),
                "OfferingRejected": gpt_data.get("OfferingRejected"),
                "AfterListeningOfferRejected": gpt_data.get("AfterListeningOfferRejected"),
                "SaleDone": gpt_data.get("SaleDone"),

                "OpeningPitchContext": gpt_data.get("OpeningPitchContext"),
                "OfferedPitchContext": gpt_data.get("OfferedPitchContext"),
                "ObjectionHandlingContext": gpt_data.get("ObjectionHandlingContext"),
                "PrepaidPitchContext": gpt_data.get("PrepaidPitchContext"),

                "FileName": row["recording_path"],

                "Category": gpt_data.get("Category"),
                "SubCategory": gpt_data.get("SubCategory"),
                "CustomerObjectionCategory": gpt_data.get("CustomerObjectionCategory"),
                "CustomerObjectionSubCategory": gpt_data.get("CustomerObjectionSubCategory"),
                "AgentRebuttalCategory": gpt_data.get("AgentRebuttalCategory"),
                "AgentRebuttalSubCategory": gpt_data.get("AgentRebuttalSubCategory"),

                "ProductOffering": gpt_data.get("ProductOffering"),
                "DiscountType": gpt_data.get("DiscountType"),

                "OpeningPitchCategory": json.dumps(
                    gpt_data.get("OpeningPitchCategory") or []
                ),

                "ContactSettingContext": gpt_data.get("ContactSettingContext"),
                "ContactSettingCategory": gpt_data.get("ContactSettingCategory"),
                "ContactSetting2": gpt_data.get("ContactSetting2"),

                "Feedback_Category": gpt_data.get("Feedback_Category"),
                "FeedbackContext": gpt_data.get("FeedbackContext"),
                "Feedback": gpt_data.get("Feedback"),

                "Age": gpt_data.get("Age"),
                "ConsumptionType": gpt_data.get("ConsumptionType"),
                "AgeofConsumption": gpt_data.get("AgeofConsumption"),
                "ReasonforQuitting": gpt_data.get("ReasonforQuitting"),

                "Sale_Pitch_Discount_Structure": gpt_data.get("Sale_Pitch_Discount_Structure"),
                "Limited_Time_Offer": gpt_data.get("Limited_Time_Offer"),
                "Snapmint_Pitch": gpt_data.get("Snapmint_Pitch"),

                "Feedback_Capture": gpt_data.get("Feedback_Capture"),
                "Acknowledgement": gpt_data.get("Acknowledgement"),
                "Apology_Assurance": gpt_data.get("Apology_Assurance"),
                "Pronunciation_Skills_Checklist": gpt_data.get("Pronunciation_Skills_Checklist"),
                "Product_Appreciation": gpt_data.get("Product_Appreciation"),

                "Customer_Details_Confirmation": gpt_data.get("Customer_Details_Confirmation"),
                "Delivery_TAT": gpt_data.get("Delivery_TAT"),
                "Order_Consent": gpt_data.get("Order_Consent"),
                "Reconfirmation": gpt_data.get("Reconfirmation"),
                "Order_Summary": gpt_data.get("Order_Summary"),

                "Further_Assistance": gpt_data.get("Further_Assistance"),
                "Call_Closing": gpt_data.get("Call_Closing"),

                "Product_Description_Guideline": gpt_data.get("Product_Description_Guideline"),
                "Alternative_Suggestion": gpt_data.get("Alternative_Suggestion"),
                "Reason_for_Not_Placing_Order": gpt_data.get("Reason_for_Not_Placing_Order"),
                "Pricing_and_Discount_Structure": gpt_data.get("Pricing_and_Discount_Structure"),

                "entrydate": datetime.now()
            }

            columns = ", ".join(insert_data.keys())
            placeholders = ", ".join(["%s"] * len(insert_data))

            audit_cur.execute(
                f"INSERT INTO CallDetails ({columns}) VALUES ({placeholders})",
                list(insert_data.values())
            )

            audit_conn.commit()

            dialer_conn = get_connection(DIALER_DB)
            dialer_cur = dialer_conn.cursor(dictionary=True)

            # ✅ mark processed
            dialer_cur.execute(
                "UPDATE call_logs SET flag=1 WHERE id=%s",
                (row["id"],)
            )

            logging.info(f"✅ Processed outbound call {row['id']}")

        except Exception as e:
            logging.error(f"Worker error: {e}")

        finally:
            try:
                if dialer_cur:
                    dialer_cur.close()
                if dialer_conn:
                    dialer_conn.close()
                if audit_cur:
                    audit_cur.close()
                if audit_conn:
                    audit_conn.close()
            except:
                pass

        time.sleep(2)


# ---------- RUN ----------
if __name__ == "__main__":
    logging.info("🚀 Outbound CallDetails Worker Started")
    worker_loop()