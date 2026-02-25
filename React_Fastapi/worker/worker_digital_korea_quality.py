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

# ---------- DB CONFIGS ----------
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
    "database": "db_audit"
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
            logging.error("Recording URL missing")
            return ""

        audio_res = requests.get(audio_url, timeout=20)

        if audio_res.status_code != 200:
            logging.error(f"Recording fetch failed: {audio_res.status_code}")
            return ""

        if len(audio_res.content) < 1000:
            logging.error("Audio file too small / empty")
            return ""

        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
        params = {"punctuate": "true", "model": "nova"}

        res = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers=headers,
            params=params,
            data=audio_res.content
        )

        if res.status_code != 200:
            logging.error(f"Deepgram API error: {res.text}")
            return ""

        transcript = (
            res.json()
            .get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
            .get("transcript", "")
        )

        return transcript.strip()

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


prompt_conn = None
prompt_cur = None


def get_prompt(client_id):
    global prompt_conn, prompt_cur

    try:
        if not prompt_conn or not prompt_conn.is_connected():
            prompt_conn = mysql.connector.connect(**PROMPT_DB)
            prompt_cur = prompt_conn.cursor(dictionary=True)

        prompt_cur.execute("""
            SELECT Prompt
            FROM tbl_prompt
            WHERE ClientId = %s
            AND status = 1
            ORDER BY id DESC
            LIMIT 1
        """, (client_id,))

        row = prompt_cur.fetchone()
        return row["Prompt"] if row else ""

    except Exception as e:
        logging.error(f"Prompt DB error: {e}")
        return ""


def safe_int(value, default=0):
    try:
        if value in ("", None):
            return default
        return int(value)
    except:
        return default


def safe_timestamp(dt):
    try:
        if not dt:
            return 0
        return int(dt.timestamp())
    except:
        return 0


# ---------- WORKER ----------
def worker_loop():
    dialer_conn = mysql.connector.connect(**DIALER_DB, autocommit=True)
    dialer_cur = dialer_conn.cursor(dictionary=True)

    while True:
        audit_conn = None
        audit_cur = None

        if not dialer_conn.is_connected():
            dialer_conn.reconnect()

        dialer_cur.execute("""
            SELECT *
            FROM cdr_du_digital_korea
            WHERE flag = 0
            AND vendor_lead_code IN (
              'South_Korea','South_Korea_E','South_Korea_H',
              'Thailand','Thailand_E','Thailand_H'
            )
            ORDER BY id ASC
            LIMIT 1;
        """)

        row = dialer_cur.fetchone()
        if not row:
            logging.info("No new records. Sleeping...")
            time.sleep(10)
            continue

        try:
            vendor = row["vendor_lead_code"]

            if vendor in ("South_Korea", "South_Korea_E", "South_Korea_H"):
                client_id = "473"
            elif vendor in ("Thailand", "Thailand_E", "Thailand_H"):
                client_id = "474"
            else:
                logging.error("Unknown vendor_lead_code")
                continue

            prompt = get_prompt(client_id)
            if not prompt:
                logging.error(f"No prompt for client {client_id}")
                continue

            transcription = deepgram_transcribe(row["recording_url"])

            sql = """
            INSERT INTO call_quality_assessment (
            ClientId, MobileNo, User, lead_id, CallDate, Campaign,
            start_epoch, end_epoch,
            length_in_sec, Transcribe_Text,

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
            %s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,
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
            """

            if not transcription:
                logging.warning(f"Empty transcription for ID {row['id']}")

                audit_conn = mysql.connector.connect(**AUDIT_DB)
                audit_cur = audit_conn.cursor()

                start_epoch = safe_timestamp(row.get("CallDate"))
                duration = safe_int(row.get("CallDurationSecond"))
                end_epoch = start_epoch + duration

                audit_cur.execute(sql, (

                    client_id,
                    row["PhoneNumber"],
                    row["AgentName"],
                    row["LeadId"],
                    row["CallDate"],
                    row["CampaignName"],
                    start_epoch,
                    end_epoch,
                    duration,
                    "",  # transcription empty

                    None, None, None, None,  # classification

                    None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,

                    0, 0, 0,  # score fields

                    None,

                    None, None, None, None,

                    None, 0, None, 0, None, 0, None, 0,

                    None, None, None, None, None, None, None,

                    None, None,

                    None, None, None, None, None, None, None,

                    None, None, None, None, None, None, None
                ))

                audit_conn.commit()

                dialer_cur.execute(
                    "UPDATE cdr_du_digital_korea SET flag = 2 WHERE id = %s",
                    (row["id"],)
                )
                dialer_conn.commit()

                audit_cur.close()
                audit_conn.close()

                continue

            gpt_data = send_to_gpt(f"{prompt}\n\nConversation:\n{transcription}")

            quality = gpt_data.get("quality_parameters", {})
            sentiment = gpt_data.get("sentiment_analysis", {})
            classification = gpt_data.get("classification", {})
            competitor = gpt_data.get("competitor_analysis", {})
            fraud = gpt_data.get("fraud_metrics", {})
            fraud_text = gpt_data.get("fraud_metrics_conversation", {})

            audit_conn = mysql.connector.connect(**AUDIT_DB)
            audit_cur = audit_conn.cursor()

            start_epoch = safe_timestamp(row.get("CallDate"))
            duration = safe_int(row.get("CallDurationSecond"))
            end_epoch = start_epoch + duration

            audit_cur.execute(sql, (

                client_id,
                row["PhoneNumber"],
                row["AgentName"],
                row["LeadId"],
                row["CallDate"],
                row["CampaignName"],
                start_epoch,
                end_epoch,
                duration,
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
                quality.get(
                    "Did the agent provide a proper closure, including asking if the customer has further concerns?"),
                quality.get("Did the agent express empathy using keywords?"),

                quality.get("total_score"),
                quality.get("max_score"),
                quality.get("quality_percentage"),

                ", ".join(gpt_data.get("areas_for_improvement", [])),

                ", ".join(sentiment.get("top_positive_words", [])),
                ", ".join(sentiment.get("top_negative_words", [])),
                ", ".join(sentiment.get("top_positive_words_agent", [])),
                ", ".join(sentiment.get("top_negative_words_agent", [])),

                ", ".join(sentiment.get("cuss_words", {}).get("agent", {}).get("english", {}).get("list", [])),
                sentiment.get("cuss_words", {}).get("agent", {}).get("english", {}).get("count"),
                ", ".join(sentiment.get("cuss_words", {}).get("agent", {}).get("hindi", {}).get("list", [])),
                sentiment.get("cuss_words", {}).get("agent", {}).get("hindi", {}).get("count"),
                ", ".join(sentiment.get("cuss_words", {}).get("customer", {}).get("english", {}).get("list", [])),
                sentiment.get("cuss_words", {}).get("customer", {}).get("english", {}).get("count"),
                ", ".join(sentiment.get("cuss_words", {}).get("customer", {}).get("hindi", {}).get("list", [])),
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
                fraud_text.get("Policy Communication Failure Text")

            ))

            audit_conn.commit()

            dialer_cur.execute("UPDATE cdr_du_digital_korea SET flag = 1 WHERE id = %s", (row["id"],))
            dialer_conn.commit()

            logging.info(f"Processed ID={row['id']} client={client_id}")

        except Exception as e:
            logging.error(f"Error: {e}")
            dialer_conn.rollback()

        finally:
            if audit_cur:
                audit_cur.close()
            if audit_conn:
                audit_conn.close()

        time.sleep(2)


if __name__ == "__main__":
    logging.info("Digital Korea Quality Worker Started")
    worker_loop()
