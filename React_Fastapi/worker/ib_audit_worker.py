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
            "model": "nova-2",
            "detect_language": "true",
            "diarize": "true",
            "smart_format": "true",
            "punctuate": "true"
        }

        res = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers=headers,
            params=params,
            data=audio_bytes,
            timeout=(30, 600)
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



# import tempfile
# from faster_whisper import WhisperModel
#
# model = WhisperModel(
#     "small",
#     device="cpu",
#     compute_type="int8",
#     cpu_threads=4
# )

# def whisper_transcribe(audio_url: str) -> str:
#     try:
#         if not audio_url:
#             return ""
#
#         session = requests.Session()
#
#         headers = {
#             "User-Agent": "Mozilla/5.0"
#         }
#
#         r = session.get(
#             audio_url,
#             headers=headers,
#             timeout=120,
#             verify=False
#         )
#
#         if r.status_code != 200:
#             logging.error(f"Unable to download audio: {r.status_code}")
#             return ""
#
#         suffix = ".wav"
#
#         if audio_url.lower().endswith(".mp3"):
#             suffix = ".mp3"
#         elif audio_url.lower().endswith(".ogg"):
#             suffix = ".ogg"
#
#         from pydub import AudioSegment
#
#         # Save original download
#         with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
#             f.write(r.content)
#             audio_path = f.name
#
#         # Convert to 16 kHz mono WAV
#         wav_path = audio_path.rsplit(".", 1)[0] + ".wav"
#
#         audio = AudioSegment.from_file(audio_path)
#
#         logging.info(
#             f"Original: rate={audio.frame_rate}, "
#             f"channels={audio.channels}, "
#             f"dBFS={audio.dBFS:.2f}"
#         )
#
#         audio = (
#             audio
#             .set_frame_rate(16000)
#             .set_channels(1)
#         )
#
#         audio.export(wav_path, format="wav")
#
#         logging.info(f"Converted WAV: {wav_path}")
#
#         start = time.time()
#
#         segments, info = model.transcribe(
#             wav_path,
#             beam_size=5,
#             best_of=5,
#             vad_filter=False,
#             condition_on_previous_text=True,
#             language=None
#         )
#
#         logging.info(f"Whisper took {time.time() - start:.2f} seconds")
#
#         logging.info(
#             f"Language={info.language}, Probability={info.language_probability:.2f}"
#         )
#
#         segments = list(segments)
#
#         logging.info(f"Segments: {len(segments)}")
#
#         for s in segments[:10]:
#             logging.info(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
#
#         transcript = " ".join(s.text for s in segments)
#
#         for path in (audio_path, wav_path):
#             try:
#                 os.remove(path)
#             except Exception:
#                 pass
#
#         return transcript.strip()
#
#     except Exception as e:
#         logging.exception(e)
#         return ""


import time
import tempfile
from pydub import AudioSegment

GPU_WHISPER_URL = "http://103.35.164.249:8010/transcribe"


def whisper_transcribe(audio_url: str) -> str:
    try:

        if not audio_url:
            return ""

        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = session.get(
            audio_url,
            headers=headers,
            timeout=120,
            verify=False
        )

        if r.status_code != 200:
            logging.error(f"Unable to download audio: {r.status_code}")
            return ""

        suffix = ".wav"

        if audio_url.lower().endswith(".mp3"):
            suffix = ".mp3"
        elif audio_url.lower().endswith(".ogg"):
            suffix = ".ogg"

        # Save downloaded recording
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(r.content)
            audio_path = f.name

        wav_path = audio_path.rsplit(".", 1)[0] + ".wav"

        from pydub.effects import normalize

        audio = AudioSegment.from_file(audio_path)

        audio = normalize(audio)

        logging.info(
            f"Original: rate={audio.frame_rate}, "
            f"channels={audio.channels}, "
            f"dBFS={audio.dBFS:.2f}"
        )

        audio = (
            audio
            .set_frame_rate(16000)
            .set_channels(1)
            .set_sample_width(2)
        )

        audio.export(
            wav_path,
            format="wav",
            parameters=[
                "-acodec", "pcm_s16le"
            ]
        )

        logging.info(f"Converted WAV: {wav_path}")

        # -----------------------------
        # Send WAV to GPU Whisper Server
        # -----------------------------
        start = time.time()

        with open(wav_path, "rb") as f:

            response = requests.post(
                GPU_WHISPER_URL,
                files={
                    "file": ("audio.wav", f, "audio/wav")
                },
                timeout=600
            )

        response.raise_for_status()

        result = response.json()

        logging.info(
            f"GPU Whisper took {time.time()-start:.2f}s"
        )

        logging.info(
            f"Language={result['language']} "
            f"Probability={result['probability']}"
        )

        transcript = result.get("transcript", "").strip()

        return transcript

    except Exception as e:
        logging.exception(e)
        return ""

    finally:

        for path in [locals().get("audio_path"), locals().get("wav_path")]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass



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

            # transcription = deepgram_transcribe(row["recording_path"])
            transcription = whisper_transcribe(row["recording_path"])

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
                    row["call_id"],
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
            customer_voc = gpt_data.get("customer_voc", {})

            # --------------------------------------------------
            # 🚀 FULL INSERT (MATCHING YOUR MAIN WORKER)
            # --------------------------------------------------
            audit_cur.execute("""
                INSERT INTO call_quality_assessment (
                    ClientId, MobileNo, lead_id, User, CallDate,
                    start_epoch, end_epoch, length_in_sec, Transcribe_Text,

                    scenario, scenario1, scenario2, scenario3,                    
                    Social_Media_Phone_Number_Order_ID_Email_ID,

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
                    further_assistance_offered,
                    proper_call_closure,
                    express_empathy,
                    customer_concern_acknowledged,
                    proper_transfer_and_language,
                    case_escalated_correctly,
                    address_recorded_completely,
                    correct_and_complete_information,
                    upselling_or_offers_suggested,
                    fraud_and_data_security_compliance,
                    proper_document_and_video_request_handling,

                    total_score, max_score, quality_percentage,

                    areas_for_improvement,

                    top_positive_words,
                    top_negative_words,
                    top_positive_words_agent,
                    top_negative_words_agent,
                    
                    customer_voc_logistic_positive,
                    customer_voc_logistic_negative,
                    customer_voc_agent_positive,
                    customer_voc_agent_negative,
                    customer_voc_product_positive,
                    customer_voc_product_negative,

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
                    fraud_detected_sentence,

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
                    Policy_Communication_Failure_Text,
                    call_recording
                )
                VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,
                    %s,%s,%s,
                    %s,
                    %s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s
                )
            """, (

                client_id,
                row["call_id"],
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
                classification.get("Social_Media_Phone_Number_Order_ID_Email_ID"),

                quality.get("Evaluate whether the agent answered or greeted the customer within 5 seconds of the call being connected. If the agent responded promptly within 5 seconds, assign 1. Assign 0 only if the initial response or greeting was delayed beyond 5 seconds without a valid system-related reason. If the response time cannot be fairly evaluated due to recording limitations, missing call connection audio, or technical issues, assign 1."),
                quality.get("Evaluate whether the agent maintained a professional, courteous, and customer-focused demeanor throughout the conversation. The agent should communicate confidently, remain calm and respectful, avoid arguing, raising their voice, using inappropriate language, or displaying frustration, and consistently represent the company's standards of professionalism. The agent should also maintain a positive attitude, use appropriate business etiquette, and stay focused on resolving the customer's query. Minor conversational variations should not be considered a failure if the overall interaction remains professional. Assign 1 if the agent maintained professionalism throughout the call. Assign 0 only if the agent displayed unprofessional behavior, inappropriate language, disrespect, impatience, or conduct that negatively impacted the customer experience. If the parameter cannot be fairly evaluated due to poor audio quality or recording issues, assign 1."),
                quality.get("Evaluate whether the agent appropriately expressed assurance or appreciation during the conversation whenever relevant. This includes thanking the customer for their patience, feedback, or information, and providing reassuring statements such as 'I understand', 'Don't worry', 'Rest assured', 'I'll help you with this', or similar phrases that build customer confidence. The agent is not required to use exact phrases, but should convey genuine appreciation or assurance where appropriate. If the conversation did not present a situation where assurance or appreciation was reasonably expected, assign 1. Assign 0 only if the parameter was applicable and the agent failed to provide any appropriate assurance or appreciation during the interaction."),
                quality.get("Evaluate whether the agent spoke with clear pronunciation, proper articulation, and an understandable pace throughout the conversation. The agent should avoid mumbling, slurring words, speaking too fast or too slowly, and should maintain a clear, confident, and professional tone that is easy for the customer to understand. Minor accent differences should not be considered an issue if the speech remains understandable. Assign 1 if the agent's pronunciation and clarity were satisfactory throughout the call. Assign 0 only if poor pronunciation, unclear speech, excessive mumbling, or an inappropriate speaking pace made the conversation difficult to understand. If audio quality or recording issues prevent a fair evaluation, assign 1."),
                quality.get("Evaluate whether the agent maintained an enthusiastic, confident, and engaging tone throughout the conversation. The agent should sound energetic, positive, and interested while speaking fluently without unnecessary hesitation, excessive filler words (such as 'uh', 'um', 'like'), repeated words, long pauses, or frequent fumbling. Minor natural pauses or brief hesitations should not be considered a failure. Assign 1 if the agent communicated confidently and maintained a professional level of enthusiasm with no significant fumbling. Assign 0 only if excessive hesitation, repeated fumbling, lack of confidence, or a noticeably dull or disengaged tone negatively impacted the customer interaction. If the parameter cannot be fairly evaluated due to poor audio quality or recording issues, assign 1."),
                quality.get("Evaluate whether the agent demonstrated active listening throughout the conversation by allowing the customer to complete their statements without unnecessary interruptions, acknowledging the customer's queries or concerns appropriately, asking relevant probing or clarifying questions when needed, and responding accurately based on the customer's inputs. The agent should avoid ignoring customer statements, giving irrelevant responses, or repeatedly asking for information that was already provided. Minor interruptions due to natural conversation flow should not be considered a failure. Assign 1 if the agent consistently demonstrated active listening and responded appropriately. Assign 0 only if the agent frequently interrupted, failed to acknowledge or understand the customer's inputs, ignored key information, or responded in a way that indicated poor listening. If the parameter cannot be fairly evaluated due to poor audio quality or recording issues, assign 1."),
                quality.get("Evaluate whether the agent maintained a polite, respectful, and professional tone throughout the conversation. The agent should use courteous language, avoid rude, dismissive, argumentative, impatient, or sarcastic remarks, and interact with the customer in a calm and respectful manner, even in challenging situations. Minor variations in tone should not be considered a failure if the overall interaction remains professional. Assign 1 if the agent consistently maintained politeness and showed no signs of sarcasm, disrespect, or inappropriate behavior. Assign 0 only if the agent used rude, sarcastic, disrespectful, dismissive, or unprofessional language or tone that negatively impacted the customer interaction. If the parameter cannot be fairly evaluated due to poor audio quality or recording issues, assign 1."),
                quality.get("Evaluate whether the agent communicated using grammatically correct, clear, and professionally structured language throughout the conversation. The agent should use coherent and meaningful sentences while avoiding significant grammatical mistakes, incorrect sentence construction, or confusing language that could affect customer understanding. Minor spoken-language errors, regional language influences, or informal conversational expressions should not be considered a failure if the overall communication remains clear, natural, and professional. Assign 1 if the agent's grammar was generally correct and did not negatively impact communication. Assign 0 only if frequent or major grammatical errors made the conversation difficult to understand or appeared unprofessional. If the parameter cannot be fairly evaluated due to poor audio quality or recording issues, assign 1."),
                quality.get("Evaluate whether the agent asked relevant and appropriate probing questions to fully understand the customer's issue, requirement, or concern before providing a solution. The agent should gather all necessary information without asking unnecessary or repetitive questions. Assign 1 if the agent adequately probed to understand the customer's needs. Assign 0 only if the agent failed to collect essential information, asked irrelevant questions, or attempted to resolve the issue without sufficient understanding. If issue probing was not required for the call, assign 1."),
                quality.get("If the agent placed the customer on hold, verify whether the agent requested permission, informed the customer about the reason for the hold, and thanked the customer after returning from hold. If no hold was required during the call, assign 1. Assign 0 only if the hold procedure was applicable and the agent failed to follow the required process."),
                quality.get("Evaluate whether the agent avoided unnecessary periods of silence during the conversation. Continuous dead air should not exceed 10 seconds unless the customer was informed beforehand (e.g., the agent requested permission to place the customer on hold or explained that they were checking information). Assign 1 if there were no unexplained periods of silence exceeding 10 seconds, or if any extended silence was properly communicated to the customer. Assign 0 only if unnecessary and unexplained dead air exceeding 10 seconds occurred, negatively impacting the customer experience. If the parameter cannot be fairly evaluated due to recording limitations, poor audio quality, or missing portions of the call, assign 1."),
                quality.get("Evaluate whether, before ending the conversation, the agent proactively offered additional assistance by asking if the customer needed any further help or had any other questions (e.g., 'Is there anything else I can help you with today?', 'Do you need assistance with anything else?', or equivalent statements). The agent is not required to use the exact wording, but the intent to offer further assistance should be clearly conveyed. If offering further assistance was not applicable due to the customer disconnecting unexpectedly or the call ending for reasons beyond the agent's control, assign 1. Assign 0 only if the parameter was applicable and the agent ended the conversation without offering any additional assistance."),
                quality.get("Evaluate whether the agent concluded the conversation in a professional, courteous, and customer-friendly manner. A proper call closure should include confirming that the customer's query or request has been addressed (where applicable), thanking the customer for their time, patience, or business, and ending the conversation with a polite closing statement such as 'Have a great day', 'Thank you for calling', or an equivalent professional farewell. The agent is not required to use these exact phrases, but the intent to close the conversation professionally should be evident. Is there anything else I can assist you with ? If the customer disconnected unexpectedly or ended the call before the agent had a reasonable opportunity to provide a proper closing, assign 1. Assign 0 only if the agent had the opportunity to close the call but ended it abruptly, omitted a professional closing, or used an inappropriate or unprofessional closing."),
                quality.get("Did the agent express empathy using keywords?"),
                quality.get("If the customer expressed a concern, complaint, issue, or dissatisfaction, verify whether the agent acknowledged it by expressing empathy, assurance, or appreciation using phrases such as 'I understand your concern', 'I am sorry', 'Thank you for informing us', 'Rest assured', etc. If no customer concern was raised during the call, assign 1. Assign 0 only if the parameter was applicable and the agent failed to acknowledge the concern."),
                quality.get("If the call required a transfer, verify whether the agent informed the customer about the transfer, used appropriate language, and obtained the customer's consent whenever applicable. If no transfer was required during the call, assign 1. Assign 0 only if the parameter was applicable and the agent failed to follow the required process."),
                quality.get("If the customer's issue required escalation, complaint registration, or service request creation, verify whether the agent clearly informed the customer about the actions being taken. If escalation was not required during the call, assign 1. Assign 0 only if the parameter was applicable and the agent failed to communicate the escalation process correctly."),
                quality.get("If address collection, verification, or confirmation was required for resolving the customer's issue, verify whether the agent accurately collected and confirmed the complete address. If address verification was not required during the call, assign 1. Assign 0 only if the parameter was applicable and the address was incomplete or incorrect."),
                quality.get("Verify whether the agent provided correct, accurate, and complete information throughout the call according to company policy. This parameter is applicable to all calls. Assign 1 if the information provided was accurate and complete; otherwise assign 0."),
                quality.get("If there was a suitable opportunity to recommend relevant products, offers, combos, discounts, coupon codes, premium variants, or complementary products, verify whether the agent made an appropriate recommendation. If upselling was not applicable for the call type (such as complaints, refunds, repeat complaints, escalations, or service-only interactions), assign 1. Assign 0 only if the parameter was applicable and the agent missed the opportunity."),
                quality.get("Evaluate whether the agent fully complied with fraud prevention and data security guidelines throughout the conversation. The agent must never request, encourage, or collect prohibited confidential information such as OTPs, UPI PINs, ATM/Debit/Credit Card PINs, CVV numbers, internet banking passwords, full card numbers (unless explicitly permitted by company policy), security answers, or any authentication credentials. The agent must not ask customers to transfer money to personal accounts, install unauthorized applications, click suspicious links, share screen access without authorization, or disclose any confidential information unrelated to the service request. Additionally, the agent must not make misleading statements, impersonate another organization, or provide false assurances. Assign 1 if the agent remained fully compliant with fraud prevention and data security policies. Assign 0 only if any fraudulent, deceptive, or unauthorized request for sensitive information or security credentials was made during the call."),
                quality.get("Evaluate whether the agent correctly handled the customer's concern by requesting and guiding the customer to provide the required supporting documents and evidence. The agent should appropriately ask whether the customer has created an unboxing video and, if not, instruct the customer to create a short video showing the concern and share it along with the invoice through the designated company email ID or approved communication channel. The agent should clearly explain that the submitted details, unboxing video, or invoice must be complete, clear, and properly visible for verification. If the previously submitted details, video, or invoice are incomplete, unclear, or improper, the agent should inform the customer of the issue and request the correct or complete documents again. The agent may also explain that a complaint or request cannot be raised until the required and proper details/documents are received. Where applicable, the agent should communicate that an update will be provided within 24 to 48 hours after receiving the required information. Equivalent Hindi, English, and Hinglish statements should be considered valid. Examples include: 'Sir, Apko 24 to 48 hour me connect krna hota hai agar koi bhi issue hota h product se related', 'Sir, kya aapne unboxing video create ki hai?', 'Agar unboxing video create nahi ki hai toh ek short video create kar lijiye aur invoice ke saath share kar dijiye', 'Humari mail ID par share kar dijiye', '24 to 48 hours mein update share kar diya jayega', 'Aapne jo details share ki hain woh proper nahi hain', 'Unboxing proper nahi hai', 'Invoice show nahi ho raha hai', 'Invoice aur video proper share karein', 'Proper details receive hone ke baad request raise ki jayegi', 'Bina proper details ke complaint raise nahi kar paunga/paungi, maaf chahunga/chahungi'. The agent does not need to use the exact wording; semantically equivalent statements are acceptable. Assign 1 if the agent appropriately requested, explained, or guided the customer regarding the required video, invoice, details, resubmission, complaint/request process, or applicable 24â€“48 hour update. Assign 0 only if the agent failed to provide the required guidance when it was applicable. If the required documents or video were not relevant to the conversation, assign 1. When this parameter is applicable and the agent makes any relevant statement, extract the EXACT sentence or phrase spoken by the agent that supports this parameter. Preserve the original wording exactly as it appears in the transcript, including Hindi, English, or Hinglish wording. Do not paraphrase, translate, summarize, or correct the extracted statement. If multiple relevant statements are present, return all relevant statements."),

                quality.get("total_score"),
                quality.get("max_score"),
                quality.get("quality_percentage"),

                safe_join(gpt_data.get("areas_for_improvement")),

                safe_join(sentiment.get("top_positive_words")),
                safe_join(sentiment.get("top_negative_words")),
                safe_join(sentiment.get("top_positive_words_agent")),
                safe_join(sentiment.get("top_negative_words_agent")),

                customer_voc.get("Customer VOC Logistic Positive"),
                customer_voc.get("Customer VOC Logistic Negative"),
                customer_voc.get("Customer VOC Agent Positive"),
                customer_voc.get("Customer VOC Agent Negative"),
                customer_voc.get("Customer VOC Product Positive"),
                customer_voc.get("Customer VOC Product Negative"),

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
                gpt_data.get("fraud_detected_sentence"),

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
                row["recording_path"],
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