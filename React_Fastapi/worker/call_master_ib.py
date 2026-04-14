import mysql.connector
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback


MAX_WORKERS = 3

# ---------------- DB CONFIG ----------------
CENTRAL_DB = {
    "host": "192.168.11.6",
    "user": "root",
    "password": "dial@mas123",
    "database": "db_dialdesk"
}

TARGET_DB = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "dialer_db"
}


# ---------------- HELPERS ----------------

def get_campaign_ids(cursor, client_id):
    cursor.execute(
        "SELECT campaignid FROM registration_master WHERE company_id=%s",
        (client_id,)
    )
    return [row[0] for row in cursor.fetchall()]


def build_agent_filter(agent_users):
    if not agent_users:
        return ""
    agents = [f"'{a.strip()}'" for a in agent_users.split(",")]
    return f"AND vc.user IN ({','.join(agents)})"


def calculate_remaining(config, target_cursor):
    client_id = config["client_id"]

    # count already inserted calls
    target_cursor.execute("""
        SELECT COUNT(*) 
        FROM call_logs 
        WHERE client_id = %s
        AND call_type = 'inbound'
        AND created_at >= CURDATE()
        AND created_at < CURDATE() + INTERVAL 1 DAY
    """, (client_id,))

    used = target_cursor.fetchone()[0]

    total = config["total_audit_call_count"]
    remaining = total - used

    agents = [a.strip() for a in (config["agent_users"] or "").split(",") if a.strip()]

    return max(remaining, 0), agents


def build_recording_url_expr(dialer_ip):
    ip_underscore = dialer_ip.replace(".", "_")

    # 🔥 special case
    if dialer_ip == "192.168.11.246":
        base_ip = "192.168.10.3"
    else:
        base_ip = "192.168.11.251"

    return f"""
        IFNULL(
            REPLACE(
                r.location,
                'http://{dialer_ip}/RECORDINGS/MP3/',
                CONCAT(
                    'http://{base_ip}/{ip_underscore}/',
                    DATE_FORMAT(DATE(vc.call_date), '%Y%m%d'),
                    '/'
                )
            ),
            ''
        ) AS file_url
    """



def process_single_config(config):
    try:
        client_id = config["client_id"]
        dialer_ip = config["dialer_server_ip"]

        if not dialer_ip:
            return

        print(f"⚡ Processing client {client_id} @ {dialer_ip}")

        # --- DB connections (per thread) ---
        central_conn = mysql.connector.connect(**CENTRAL_DB)
        central_cursor = central_conn.cursor()

        target_conn = mysql.connector.connect(**TARGET_DB)
        target_cursor = target_conn.cursor()

        dialer_conn = mysql.connector.connect(
            host=dialer_ip,
            user="root",
            password="vicidialnow",
            database="asterisk"
        )
        dialer_cursor = dialer_conn.cursor(dictionary=True)

        file_url_expr = build_recording_url_expr(dialer_ip)

        # campaign ids
        campaign_ids = get_campaign_ids(central_cursor, client_id)
        if not campaign_ids:
            return

        campaign_ids_clean = [c.strip().strip("'") for c in campaign_ids]
        campaign_ids_str = ",".join([f"'{c}'" for c in campaign_ids_clean])

        # audit logic
        remaining, agents = calculate_remaining(config, target_cursor)
        if remaining <= 0:
            print(f"⏭ Skipping client {client_id}")
            return

        # filters
        agent_filter = ""
        if agents:
            agent_list = ",".join([f"'{a}'" for a in agents])
            agent_filter = f"AND vc.user IN ({agent_list})"

        duration_filter = f"""
            AND vc.length_in_sec BETWEEN {config['min_call_duration']}
            AND {config['max_call_duration']}
        """

        time_filter = f"""
            AND TIME(vc.call_date) BETWEEN '{config['time_from']}'
            AND '{config['time_to']}'
        """

        query = f"""
            SELECT
                vc.campaign_id,
                vc.user,
                vc.call_date,
                vc.lead_id,
                vc.length_in_sec,
                vc.start_epoch,
                vc.end_epoch,
                {file_url_expr}
            FROM vicidial_closer_log vc
            LEFT JOIN recording_log r
                ON vc.lead_id = r.lead_id
               AND DATE(vc.call_date) = DATE(r.start_time)
            WHERE vc.campaign_id IN ({campaign_ids_str})
                AND vc.call_date >= CURDATE()
                AND vc.call_date < CURDATE() + INTERVAL 1 DAY
                AND vc.call_date <= DATE_SUB(NOW(), INTERVAL 15 MINUTE)
                {agent_filter}
                {duration_filter}
                {time_filter}
                AND vc.user != 'VDCL'
            ORDER BY vc.call_date DESC
            LIMIT %s
        """

        dialer_cursor.execute(query, (remaining,))
        rows = dialer_cursor.fetchall()

        if not rows:
            return

        # 🚀 BULK INSERT
        insert_query = """
            INSERT IGNORE INTO call_logs (
                client_id, lead_id, call_id, agent_id,
                start_time, end_time, call_type,
                duration, recording_path, created_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        data = []
        now = datetime.now()

        for row in rows:
            data.append((
                client_id,
                row["lead_id"],
                row["lead_id"],
                row["user"],
                datetime.fromtimestamp(row["start_epoch"]),
                datetime.fromtimestamp(row["end_epoch"]),
                config["call_type"],
                row["length_in_sec"],
                row["file_url"],
                now
            ))

        target_cursor.executemany(insert_query, data)
        target_conn.commit()

        print(f"✅ Inserted {len(data)} rows for client {client_id}")

    except Exception as e:
        print(f"❌ Error client {config['client_id']}: {e}")
        traceback.print_exc()


    finally:
        try:
            if 'dialer_cursor' in locals():
                dialer_cursor.close()
            if 'dialer_conn' in locals():
                dialer_conn.close()
            if 'target_cursor' in locals():
                target_cursor.close()
            if 'target_conn' in locals():
                target_conn.close()
            if 'central_cursor' in locals():
                central_cursor.close()
            if 'central_conn' in locals():
                central_conn.close()
        except:
            pass



# ---------------- MAIN PROCESS ----------------

def process_audit_configs():
    central_conn = mysql.connector.connect(**CENTRAL_DB)
    central_cursor = central_conn.cursor(dictionary=True)

    central_cursor.execute("""
        SELECT * FROM audit_config 
        WHERE total_audit_call_count > 0
        AND call_type = 'inbound'
    """)

    configs = central_cursor.fetchall()

    central_cursor.close()
    central_conn.close()

    # 🚀 PARALLEL EXECUTION
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_single_config, config) for config in configs]

        for future in as_completed(futures):
            future.result()


# ---------------- RUN ----------------

def run_worker():
    print("🚀 Audit Worker Started...")
    while True:
        try:
            process_audit_configs()
        except Exception as e:
            print(f"Worker error: {e}")

        print("⏳ Sleeping for 5 minutes...\n")
        time.sleep(300)  # 5 minutes


if __name__ == "__main__":
    run_worker()