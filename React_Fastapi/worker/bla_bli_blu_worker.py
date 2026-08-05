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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

# def deepgram_transcribe(audio_url):
#
#     if not audio_url:
#         return ""
#
#     try:
#         audio = requests.get(audio_url, timeout=30)
#
#         if audio.status_code != 200 or len(audio.content) < 1000:
#             logging.warning("Invalid audio")
#             return ""
#
#         headers = {
#             "Authorization": f"Token {DEEPGRAM_API_KEY}",
#             "Content-Type": "audio/mpeg"
#         }
#
#         params = {
#             "model": "nova-2",
#             "detect_language": "true",
#             "diarize": "true",
#             "smart_format": "true",
#             "punctuate": "true"
#         }
#
#         res = requests.post(
#             "https://api.deepgram.com/v1/listen",
#             headers=headers,
#             params=params,
#             data=audio.content,
#             timeout=(30, 600)
#         )
#
#         if res.status_code != 200:
#             logging.error(res.text)
#             return ""
#
#         return (
#             res.json()
#             .get("results", {})
#             .get("channels", [{}])[0]
#             .get("alternatives", [{}])[0]
#             .get("transcript", "")
#         )
#
#     except Exception as e:
#         logging.error(f"Deepgram error: {e}")
#         return ""




def deepgram_transcribe(audio_url):
    if not audio_url:
        return ""

    try:
        # Create session with retry support
        session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.mount("http://", HTTPAdapter(max_retries=retries))

        # Browser-like headers
        download_headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

        logging.info(f"Downloading audio: {audio_url}")

        audio = session.get(
            audio_url,
            headers=download_headers,
            timeout=60,
            allow_redirects=True,
            stream=False,
        )

        logging.info(
            "Download Status=%s Size=%s Type=%s URL=%s",
            audio.status_code,
            len(audio.content),
            audio.headers.get("Content-Type"),
            audio.url,
        )

        if audio.status_code != 200:
            logging.error("Download failed: %s", audio.text[:500])
            return ""

        if len(audio.content) < 1000:
            logging.error("Downloaded audio is too small (%s bytes)", len(audio.content))
            return ""

        # Optional: save failed files for debugging
        # with open("/tmp/debug.mp3", "wb") as f:
        #     f.write(audio.content)

        dg_headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": audio.headers.get("Content-Type", "audio/mpeg"),
        }

        params = {
            "model": "nova-2",
            "detect_language": "true",
            "diarize": "true",
            "smart_format": "true",
            "punctuate": "true",
        }

        logging.info("Sending audio to Deepgram...")

        res = session.post(
            "https://api.deepgram.com/v1/listen",
            headers=dg_headers,
            params=params,
            data=audio.content,
            timeout=(30, 600),
        )

        logging.info("Deepgram Status: %s", res.status_code)

        if res.status_code != 200:
            logging.error("Deepgram Error: %s", res.text)
            return ""

        data = res.json()

        transcript = (
            data.get("results", {})
                .get("channels", [{}])[0]
                .get("alternatives", [{}])[0]
                .get("transcript", "")
        )

        logging.info("Transcript length: %s", len(transcript))

        return transcript

    except Exception:
        logging.exception("Deepgram transcription failed")
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

    audit = mysql.connector.connect(**AUDIT_DB)
    acur = audit.cursor()

    prompt = get_prompt()

    if not prompt:
        logging.error("Prompt missing for client 487")
        return

    while True:

        dialer.ping(reconnect=True, attempts=3, delay=5)
        audit.ping(reconnect=True, attempts=3, delay=5)

        dcur.execute("""
            SELECT *
            FROM cdr_bla_bli_blu
            WHERE flag=0
                AND created_at >= '2026-07-31 00:00:00'
                AND total_call_duration >= 120
                AND created_at <= NOW() - INTERVAL 5 MINUTE
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

            duration_sec = row["total_call_duration"]

            start_epoch = timestamp_epoch(row["date_time"])
            end_epoch = start_epoch + duration_sec

            # Set client_id based on campaign_name
            # if row["campaign_name"] in ("Outbound", "Personal"):
            #     client_id_value = 493
            # else:
            #     client_id_value = CLIENT_ID

            insert_data = {

                "client_id": CLIENT_ID,
                "campaign_id": row["campaign_name"],
                "length_in_sec": duration_sec,
                "start_epoch": start_epoch,
                "end_epoch": end_epoch,
                "CallDate": row["date_time"],
                "AgentName": row["agent_name"],
                "MobileNo": row["customer_number"],

                "CallDisposition": row["disposition"],
                "CompetitorName": gpt_data.get("CompetitorName"),
                "TopNegativeWordsByAgent": gpt_data.get("TopNegativeWordsByAgent"),
                "TopNegativeWordsByCustomer": gpt_data.get("TopNegativeWordsByCustomer"),
                "NotInterestedReasonCallContext": gpt_data.get("NotInterestedReasonCallContext"),
                "NotInterestedBucketReason": gpt_data.get("NotInterestedBucketReason"),

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

        time.sleep(2)


# ---------------- START ----------------

if __name__ == "__main__":
    logging.info("BlaBliBlu Worker Started")
    worker()