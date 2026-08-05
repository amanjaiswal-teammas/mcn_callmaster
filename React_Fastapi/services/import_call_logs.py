import pandas as pd
import mysql.connector
from datetime import datetime
import uuid

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
# EXCEL FILE PATH
# =========================
EXCEL_FILE = r"C:\Users\User\Downloads\CdrReport_2026-08-03_10-46-25.xls"

# =========================
# MYSQL CONNECTION
# =========================
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# =========================
# READ EXCEL
# =========================
df = pd.read_html(EXCEL_FILE)[0]

# =========================
# FILTER LENGTH >= 120 SEC
# =========================
df = df[df["Length (Sec)"] >= 120]

# df = df[df["Agent Id"].astype(str).str.upper() != "VDAD"]

print(f"Total records to insert: {len(df)}")

def clean(value):
    if pd.isna(value):
        return None
    return str(value).strip()

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
    created_at
)
VALUES (
    497,
    %(lead_id)s,
    %(call_id)s,
    %(agent_id)s,
    %(start_time)s,
    %(end_time)s,
    'outbound',
    %(duration)s,
    %(recording_path)s,
    NOW()
)
"""

# =========================
# PROCESS ROWS
# =========================
inserted = 0
failed = 0

for _, row in df.iterrows():
    try:

        data = {
            "lead_id": int(row["Lead Id"]),
            "call_id": row["Phone Number"],
            "agent_id": row["Agent Id"],
            "start_time": pd.to_datetime(row["Start Time"]),
            "end_time": pd.to_datetime(row["End Time"]),
            "duration": int(row["Length (Sec)"]),
            "recording_path": row["Recordings"],
        }

        cursor.execute(query, data)
        inserted += 1

        print(f"Inserted Lead ID: {row['Lead Id']}")

    except Exception as e:
        failed += 1
        print(f"Failed row Lead ID {row.get('Lead Id')}: {e}")

# =========================
# COMMIT
# =========================
conn.commit()

print("\n========== DONE ==========")
print(f"Inserted: {inserted}")
print(f"Failed: {failed}")

# =========================
# CLOSE
# =========================
cursor.close()
conn.close()