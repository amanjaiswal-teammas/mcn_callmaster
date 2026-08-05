import pandas as pd
import mysql.connector
from datetime import datetime

# =========================
# DATABASE CONFIG
# =========================
DB_CONFIG = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "dialer_db",
}

# =========================
# XLSX FILE PATH
# =========================
EXCEL_FILE = r"C:\Users\User\Downloads\call Link.xlsx"

# =========================
# CLIENT ID
# =========================
CLIENT_ID = 498

# =========================
# MYSQL CONNECTION
# =========================
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# =========================
# READ XLSX
# =========================
df = pd.read_excel(EXCEL_FILE)

# Keep only Active leads
df = df[
    df["LeadStatus"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("active")
]

print(f"Total Active records found: {len(df)}")

# =========================
# INSERT QUERY
# =========================
query = """
INSERT INTO call_logs (
    client_id,
    lead_id,
    call_id,
    agent_id,
    start_time,
    end_time,
    call_type,
    duration,
    recording_path,
    campaign_id,
    created_at
)
VALUES (
    %(client_id)s,
    %(lead_id)s,
    %(call_id)s,
    %(agent_id)s,
    %(start_time)s,
    %(end_time)s,
    'inbound',
    %(duration)s,
    %(recording_path)s,
    %(campaign_id)s,
    NOW()
)
"""

# =========================
# PROCESS ROWS
# =========================
inserted = 0
failed = 0
duplicates = 0

for _, row in df.iterrows():
    try:
        # Skip empty lead IDs
        if pd.isna(row["UniqueLeadId"]):
            continue

        # Parse datetime
        start_time = pd.to_datetime(
            row["ConnectedTime"],
            format="%d-%m-%Y %H:%M",
            errors="coerce"
        )

        end_time = pd.to_datetime(
            row["DisConnectedTime"],
            format="%d-%m-%Y %H:%M",
            errors="coerce"
        )

        if pd.isna(start_time) or pd.isna(end_time):
            raise Exception("Invalid datetime")

        # Convert HH:MM:SS to seconds
        # duration_str = str(row["CallDurationMinutes"]).strip()
        #
        # try:
        #     h, m, s = map(int, duration_str.split(":"))
        #     duration = (h * 3600) + (m * 60) + s
        # except:
        #     duration = 0

        # Calculate duration in seconds from ConnectedTime and DisConnectedTime
        duration = int((end_time - start_time).total_seconds())

        # Prevent negative durations
        if duration < 0:
            duration = 0

        data = {
            "client_id": CLIENT_ID,
            "lead_id": str(row["UniqueLeadId"]).strip(),
            "call_id": str(row["CallNumber"]).strip(),
            "agent_id": str(row["AgentName"]).strip(),
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "recording_path": str(row["RecordingUrl"]).strip(),
            "campaign_id": str(row["CampaignId"]).strip(),
        }

        cursor.execute(query, data)
        inserted += 1

        print(
            f"Inserted Lead ID: {data['lead_id']} | "
            f"Call No: {data['call_id']}"
        )

    except mysql.connector.errors.IntegrityError as e:
        # Handles UNIQUE KEY (client_id, lead_id, start_time)
        duplicates += 1
        print(
            f"Duplicate skipped: "
            f"{row.get('UniqueLeadId')} | {e}"
        )

    except Exception as e:
        failed += 1
        print(
            f"Failed row Lead ID "
            f"{row.get('UniqueLeadId')}: {e}"
        )

# =========================
# COMMIT
# =========================
conn.commit()

print("\n========== DONE ==========")
print(f"Inserted   : {inserted}")
print(f"Duplicates : {duplicates}")
print(f"Failed     : {failed}")

# =========================
# CLOSE
# =========================
cursor.close()
conn.close()