import time
import mysql.connector
import logging
import os
import requests
import json
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ---------------- CONFIG ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

CLIENT_ID = 487

# ---------------- DATABASES ----------------
DIALER_DB = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "dialer_db"
}

AUDIT_DB = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "db_external"
}

PROMPT_DB = {
    "host": "192.168.11.6",
    "user": "root",
    "password": "dial@mas123",
    "database": "db_dialdesk"
}

# ---------------- HELPERS ----------------

def safe_int(v):
    try:
        return int(v)
    except:
        return 0


def time_to_seconds(t):
    try:
        if not t:
            return 0
        h, m, s = map(int, str(t).split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0


def timestamp_epoch(dt):
    try:
        return int(dt.timestamp())
    except:
        return 0


# ---------------- PROMPT ----------------

prompt_conn = None
prompt_cur = None

def get_prompt():
    global prompt_conn, prompt_cur

    try:
        if not prompt_conn or not prompt_conn.is_connected():
            prompt_conn = mysql.connector.connect(**PROMPT_DB)
            prompt_cur = prompt_conn.cursor(dictionary=True)

        prompt_cur.execute("""
            SELECT Prompt
            FROM tbl_prompt_ob
            WHERE ClientId=%s
            AND status=1
            ORDER BY id DESC
            LIMIT 1
        """, (CLIENT_ID,))

        row = prompt_cur.fetchone()
        return row["Prompt"] if row else ""

    except Exception as e:
        logging.error(f"Prompt fetch error: {e}")
        return ""


# ---------------- DEEPGRAM ----------------

def deepgram_transcribe(audio_url):

    if not audio_url:
        return ""

    try:
        audio = requests.get(audio_url, timeout=30)

        if audio.status_code != 200 or len(audio.content) < 1000:
            logging.warning("Invalid audio")
            return ""

        res = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
            params={"punctuate": "true", "model": "nova"},
            data=audio.content
        )

        if res.status_code != 200:
            logging.error(res.text)
            return ""

        return (
            res.json()
            .get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
            .get("transcript", "")
        )

    except Exception as e:
        logging.error(f"Deepgram error: {e}")
        return ""


# ---------------- GPT ----------------

def send_to_gpt(prompt):

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        content = res.choices[0].message.content

        match = re.search(r"\{[\s\S]*\}", content)
        return json.loads(match.group(0)) if match else {}

    except Exception as e:
        logging.error(f"GPT error {e}")
        return {}


# ---------------- WORKER ----------------

def worker():

    dialer = mysql.connector.connect(**DIALER_DB, autocommit=True)
    dcur = dialer.cursor(dictionary=True)

    prompt = get_prompt()

    if not prompt:
        logging.error("Prompt missing for client 487")
        return

    while True:

        dcur.execute("""
            SELECT *
            FROM cdr_bla_bli_blu
            WHERE flag=0
            ORDER BY id ASC
            LIMIT 1
        """)

        row = dcur.fetchone()

        if not row:
            logging.info("No new calls...")
            time.sleep(10)
            continue

        try:

            transcription = deepgram_transcribe(row["recording"])

            gpt_data = {}

            if transcription:
                gpt_data = send_to_gpt(
                    f"{prompt}\n\nConversation:\n{transcription}"
                )

            duration_sec = time_to_seconds(row["total_call_duration"])

            start_epoch = timestamp_epoch(row["date_time"])
            end_epoch = start_epoch + duration_sec

            audit = mysql.connector.connect(**AUDIT_DB)
            acur = audit.cursor()

            insert_data = {

                "client_id": CLIENT_ID,
                "campaign_id": row["campaign_name"],
                "length_in_sec": duration_sec,
                "start_epoch": start_epoch,
                "end_epoch": end_epoch,
                "CallDate": row["date_time"],
                "AgentName": row["agent_name"],
                "MobileNo": row["customer_number"],

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

                "FileName": row["recording"],

                "Category": gpt_data.get("Category"),
                "SubCategory": gpt_data.get("SubCategory"),
                "CustomerObjectionCategory": gpt_data.get("CustomerObjectionCategory"),
                "CustomerObjectionSubCategory": gpt_data.get("CustomerObjectionSubCategory"),
                "AgentRebuttalCategory": gpt_data.get("AgentRebuttalCategory"),
                "AgentRebuttalSubCategory": gpt_data.get("AgentRebuttalSubCategory"),

                "ProductOffering": gpt_data.get("ProductOffering"),
                "DiscountType": gpt_data.get("DiscountType"),

                "OpeningPitchCategory": json.dumps(
                    gpt_data.get("OpeningPitchCategory")
                ),

                "ContactSettingContext": gpt_data.get("ContactSettingContext"),
                "ContactSettingCategory": gpt_data.get("ContactSettingCategory"),
                "ContactSetting2": gpt_data.get("ContactSetting2"),

                "Feedback_Category": gpt_data.get("Feedback_Category"),
                "FeedbackContext": gpt_data.get("FeedbackContext"),
                "Feedback": gpt_data.get("Feedback"),

                "entrydate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            columns = ", ".join(insert_data.keys())
            placeholders = ", ".join(["%s"] * len(insert_data))
            values = list(insert_data.values())

            sql = f"INSERT INTO CallDetails ({columns}) VALUES ({placeholders})"

            acur.execute(sql, values)

            audit.commit()

            dcur.execute(
                "UPDATE cdr_bla_bli_blu SET flag=1 WHERE id=%s",
                (row["id"],)
            )

            logging.info(f"Processed Call ID {row['id']}")

        except Exception as e:
            logging.error(e)
            dialer.rollback()

        finally:
            try:
                acur.close()
                audit.close()
            except:
                pass

        time.sleep(2)


# ---------------- START ----------------

if __name__ == "__main__":
    logging.info("BlaBliBlu Worker Started")
    worker()