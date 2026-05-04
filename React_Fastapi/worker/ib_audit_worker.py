import time
import mysql.connector
import logging
import os
import requests
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ---------- CONFIG ----------
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

# ---------- DB CONFIG ----------
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
    "database": "db_audit",
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
            "Referer": audio_url
        }

        # 🔥 Retry logic (important)
        for attempt in range(3):
            try:
                audio_res = session.get(
                    audio_url,
                    headers=headers_req,
                    timeout=60,
                    verify=False   # 🔥 important for internal HTTPS (172.x)
                )

                if audio_res.status_code == 200:
                    audio_bytes = audio_res.content
                    break

                logging.warning(f"Attempt {attempt+1} failed: {audio_res.status_code}")
                time.sleep(2)

            except Exception as e:
                logging.warning(f"Retry {attempt+1} error: {e}")
                time.sleep(2)
        else:
            logging.error(f"Audio fetch failed completely: {audio_url}")
            return ""

        if not audio_bytes:
            logging.error(f"Empty audio file: {audio_url}")
            return ""

        # ✅ Detect type
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
        FROM tbl_prompt
        WHERE ClientId = %s AND status = 1
        ORDER BY id DESC LIMIT 1
    """, (client_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row["Prompt"] if row else ""


def safe_timestamp(dt):
    try:
        return int(dt.timestamp()) if dt else 0
    except:
        return 0


def safe_join(value):
    if not value:
        return ""

    if isinstance(value, list):
        cleaned = []
        for v in value:
            if isinstance(v, dict):
                # extract meaningful value from dict
                cleaned.append(str(next(iter(v.values()), "")))
            else:
                cleaned.append(str(v))
        return ", ".join(cleaned)

    return str(value)


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

            # 🔥 Fetch 1 record
            dialer_cur.execute("""
                SELECT *
                FROM call_logs
                WHERE flag = 0
                AND call_type = 'inbound'
                ORDER BY id ASC
                LIMIT 1
            """)

            row = dialer_cur.fetchone()

            # 🔥 CLOSE CONNECTION BEFORE API CALLS
            dialer_cur.close()
            dialer_conn.close()

            if not row:
                logging.info("No calls to process...")
                time.sleep(10)
                continue

            client_id = row["client_id"]

            prompt = get_prompt(client_id)
            if not prompt:
                logging.error(f"No prompt for client {client_id}")

                dialer_conn = get_connection(DIALER_DB)
                dialer_cur = dialer_conn.cursor()

                dialer_cur.execute(
                    "UPDATE call_logs SET flag = 3 WHERE id=%s",
                    (row["id"],)
                )
                continue

            transcription = deepgram_transcribe(row["recording_path"])

            start_epoch = safe_timestamp(row["start_time"])
            end_epoch = safe_timestamp(row["end_time"])

            audit_conn = get_connection(AUDIT_DB)
            audit_cur = audit_conn.cursor()

            # --------------------------------------------------
            # ❌ NO TRANSCRIPTION CASE
            # --------------------------------------------------
            if not transcription:
                logging.warning(f"No transcription for {row['id']}")

                audit_cur.execute("""
                    INSERT INTO call_quality_assessment (
                        ClientId, MobileNo, lead_id, User, CallDate,
                        start_epoch, end_epoch, length_in_sec, Transcribe_Text
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    client_id,
                    row["lead_id"],
                    row["lead_id"],
                    row["agent_id"],
                    row["start_time"],
                    start_epoch,
                    end_epoch,
                    row["duration"],
                    ""
                ))

                audit_conn.commit()

                dialer_conn = get_connection(DIALER_DB)
                dialer_cur = dialer_conn.cursor()

                dialer_cur.execute(
                    "UPDATE call_logs SET flag = 2 WHERE id=%s",
                    (row["id"],)
                )
                continue

            # --------------------------------------------------
            # 🔥 GPT CALL
            # --------------------------------------------------
            gpt_data = send_to_gpt(f"{prompt}\n\nConversation:\n{transcription}")

            quality = gpt_data.get("quality_parameters", {})
            sentiment = gpt_data.get("sentiment_analysis", {})
            classification = gpt_data.get("classification", {})
            competitor = gpt_data.get("competitor_analysis", {})
            fraud = gpt_data.get("fraud_metrics", {})
            fraud_text = gpt_data.get("fraud_metrics_conversation", {})

            # --------------------------------------------------
            # 🚀 FULL INSERT (MATCHING YOUR MAIN WORKER)
            # --------------------------------------------------
            audit_cur.execute("""
                INSERT INTO call_quality_assessment (
                    ClientId, MobileNo, lead_id, User, CallDate,
                    start_epoch, end_epoch, length_in_sec, Transcribe_Text,

                    scenario, scenario1, scenario2, scenario3,

                    call_answered_within_5_seconds,
                    professionalism_maintained,
                    assurance_or_appreciation_provided,
                    pronunciation_and_clarity,
                    enthusiasm_and_no_fumbling,
                    active_listening,
                    politeness_and_no_sarcasm,
                    proper_grammar,
                    accurate_issue_probing,
                    proper_hold_procedure,
                    dead_air_under_10_seconds,
                    proper_transfer_and_language,
                    correct_and_complete_information,
                    further_assistance_offered,
                    proper_call_closure,
                    express_empathy,

                    total_score, max_score, quality_percentage,

                    areas_for_improvement,

                    top_positive_words,
                    top_negative_words,
                    top_positive_words_agent,
                    top_negative_words_agent,

                    agent_english_cuss_words,
                    agent_english_cuss_count,
                    agent_hindi_cuss_words,
                    agent_hindi_cuss_count,
                    customer_english_cuss_words,
                    customer_english_cuss_count,
                    customer_hindi_cuss_words,
                    customer_hindi_cuss_count,

                    Competitor_Name,
                    Positive_Comparison,
                    Reason_for_Positive_Comparison,
                    Exact_Positive_Language,
                    Negative_Comparison,
                    Reason_for_Negative_Comparison,
                    Exact_Negative_Language,

                    sensetive_word,
                    sensitive_word_context,

                    data_theft_or_misuse,
                    unprofessional_behavior,
                    system_manipulation,
                    financial_fraud,
                    escalation_failure,
                    collusion,
                    policy_communication_failure,

                    Data_Theft_or_Misuse_Text,
                    Unprofessional_Behavior_Text,
                    System_Manipulation_Text,
                    Financial_Fraud_Text,
                    Escalation_Failure_Text,
                    Collusion_Text,
                    Policy_Communication_Failure_Text
                )
                VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,
                    %s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,
                    %s,%s,
                    %s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s
                )
            """, (

                client_id,
                row["lead_id"],
                row["lead_id"],
                row["agent_id"],
                row["start_time"],
                start_epoch,
                end_epoch,
                row["duration"],
                transcription,

                classification.get("scenario"),
                classification.get("scenario1"),
                classification.get("scenario2"),
                classification.get("scenario3"),

                quality.get("Did the agent follow the correct opening?"),
                quality.get("Did the agent maintain professionalism without rude behavior?"),
                quality.get("Did the agent use phrases that provide assurance or express appreciation?"),
                quality.get("Did the agent use correct pronunciation and maintain clarity?"),
                quality.get("Did the agent speak with appropriate enthusiasm without fumbling?"),
                quality.get("Did the agent actively listen without unnecessary interruptions?"),
                quality.get("Was the agent polite and free of sarcasm?"),
                quality.get("Did the agent use proper grammar?"),
                quality.get("Did the agent accurately probe to understand the issue?"),
                quality.get("Did the agent inform the customer before placing them on hold using appropriate phrases?"),
                quality.get("Did the agent thank the customer for being on line after retrieving the call?"),
                quality.get("Was the call transferred after appropriate effort and with proper language?"),
                quality.get("Did the agent provide correct and complete information?"),
                quality.get("Did the agent clearly state timelines for resolution?"),
                quality.get("Did the agent provide a proper closure, including asking if the customer has further concerns?"),
                quality.get("Did the agent express empathy using keywords?"),

                quality.get("total_score"),
                quality.get("max_score"),
                quality.get("quality_percentage"),

                safe_join(gpt_data.get("areas_for_improvement")),

                safe_join(sentiment.get("top_positive_words")),
                safe_join(sentiment.get("top_negative_words")),
                safe_join(sentiment.get("top_positive_words_agent")),
                safe_join(sentiment.get("top_negative_words_agent")),

                safe_join(sentiment.get("cuss_words", {}).get("agent", {}).get("english", {}).get("list")),
                sentiment.get("cuss_words", {}).get("agent", {}).get("english", {}).get("count"),

                safe_join(sentiment.get("cuss_words", {}).get("agent", {}).get("hindi", {}).get("list")),
                sentiment.get("cuss_words", {}).get("agent", {}).get("hindi", {}).get("count"),

                safe_join(sentiment.get("cuss_words", {}).get("customer", {}).get("english", {}).get("list")),
                sentiment.get("cuss_words", {}).get("customer", {}).get("english", {}).get("count"),

                safe_join(sentiment.get("cuss_words", {}).get("customer", {}).get("hindi", {}).get("list")),
                sentiment.get("cuss_words", {}).get("customer", {}).get("hindi", {}).get("count"),

                competitor.get("Competitor Name"),
                competitor.get("Positive Comparison"),
                competitor.get("Reason for Positive Comparison"),
                competitor.get("Exact Positive Language"),
                competitor.get("Negative Comparison"),
                competitor.get("Reason for Negative Comparison"),
                competitor.get("Exact Negative Language"),

                gpt_data.get("sensitive_word"),
                gpt_data.get("sensitive_word_context"),

                fraud.get("Data Theft or Misuse"),
                fraud.get("Unprofessional Behavior"),
                fraud.get("System Manipulation"),
                fraud.get("Financial Fraud"),
                fraud.get("Escalation Failure"),
                fraud.get("Collusion"),
                fraud.get("Policy Communication Failure"),

                fraud_text.get("Data Theft or Misuse Text"),
                fraud_text.get("Unprofessional Behavior Text"),
                fraud_text.get("System Manipulation Text"),
                fraud_text.get("Financial Fraud Text"),
                fraud_text.get("Escalation Failure Text"),
                fraud_text.get("Collusion Text"),
                fraud_text.get("Policy Communication Failure Text"),
            ))

            audit_conn.commit()

            dialer_conn = get_connection(DIALER_DB)
            dialer_cur = dialer_conn.cursor(dictionary=True)

            dialer_cur.execute(
                "UPDATE call_logs SET flag = 1 WHERE id=%s",
                (row["id"],)
            )

            logging.info(f"✅ Processed call_log ID={row['id']}")

        except Exception as e:
            logging.error(f"Worker error: {e}")
            try:
                dialer_conn.rollback()
            except:
                pass

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
    logging.info("📞 Call Logs Audit Worker Started")
    worker_loop()