# import mysql.connector
#
# # SOURCE DB
# source_conn = mysql.connector.connect(
#     host="192.168.10.23",
#     user="root",
#     password="vicidialnow",
#     database="reginald"
# )
#
# # DESTINATION DB
# dest_conn = mysql.connector.connect(
#     host="192.168.10.37",
#     user="root",
#     password="India@1234",
#     database="db_email"
# )
#
# source_cursor = source_conn.cursor(dictionary=True)
# dest_cursor = dest_conn.cursor()
#
# BATCH_SIZE = 2000
# last_id = 0
# total = 0
#
# while True:
#
#     source_cursor.execute("""
#         SELECT
#             id,
#             received_at_email,
#             subject,
#             status,
#             created_at,
#             updated_at
#         FROM tickets
#         WHERE id > %s
#         ORDER BY id
#         LIMIT %s
#     """, (last_id, BATCH_SIZE))
#
#     rows = source_cursor.fetchall()
#
#     if not rows:
#         break
#
#     insert_data = []
#
#     for row in rows:
#
#         # STATUS MAPPING
#         if row["status"] == "open":
#             status = "Open"
#         elif row["status"] == "closed":
#             status = "Closed"
#         else:
#             status = "Pending"
#
#         insert_data.append((
#             row["id"],
#             row["received_at_email"],
#             None,
#             row["subject"],
#             status,
#             None,   # assigned_to set NULL because FK users not exist
#             None,
#             None,
#             None,
#             row["created_at"],
#             row["updated_at"],
#             "email"
#         ))
#
#         last_id = row["id"]
#
#     insert_query = """
#     INSERT IGNORE INTO tickets
#     (
#         id,
#         customer_email,
#         customer_name,
#         subject,
#         status,
#         assigned_to,
#         language_id,
#         voc_id,
#         priority_id,
#         created_at,
#         updated_at,
#         channel
#     )
#     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#     """
#
#     dest_cursor.executemany(insert_query, insert_data)
#     dest_conn.commit()
#
#     total += len(insert_data)
#     print(f"Migrated: {total}")
#
# print("Migration Completed")
#
# source_cursor.close()
# dest_cursor.close()
# source_conn.close()
# dest_conn.close()





# import mysql.connector
#
# source_conn = mysql.connector.connect(
#     host="192.168.10.23",
#     user="root",
#     password="vicidialnow",
#     database="reginald"
# )
#
# dest_conn = mysql.connector.connect(
#     host="192.168.10.37",
#     user="root",
#     password="India@1234",
#     database="db_email"
# )
#
# source_cursor = source_conn.cursor(dictionary=True)
# dest_cursor = dest_conn.cursor()
#
# source_cursor.execute("""
# SELECT id, assigned_to
# FROM tickets
# WHERE assigned_to IS NOT NULL
# """)
#
# rows = source_cursor.fetchall()
#
# update_data = []
#
# for r in rows:
#     update_data.append((r["assigned_to"], r["id"]))
#
# BATCH = 2000
# for i in range(0, len(update_data), BATCH):
#     chunk = update_data[i:i+BATCH]
#     dest_cursor.executemany(
#         "UPDATE tickets SET assigned_to=%s WHERE id=%s",
#         chunk
#     )
#     dest_conn.commit()
#
# print("Assigned_to updated successfully")
#
# source_cursor.close()
# dest_cursor.close()
# source_conn.close()
# dest_conn.close()











import mysql.connector

# SOURCE DB
source_conn = mysql.connector.connect(
    host="192.168.10.23",
    user="root",
    password="vicidialnow",
    database="reginald"
)

# DEST DB
dest_conn = mysql.connector.connect(
    host="192.168.10.37",
    user="root",
    password="India@1234",
    database="db_email"
)

source_cursor = source_conn.cursor(dictionary=True)
dest_cursor = dest_conn.cursor()

BATCH = 2000
last_id = 0
total = 0

while True:

    source_cursor.execute("""
        SELECT
            r.id,
            r.ticket_id,
            r.user_id,
            r.body,
            r.created_at,
            r.email_id,
            t.subject,
            t.received_at_email AS customer_email
        FROM replies r
        JOIN tickets t ON r.ticket_id = t.id
        WHERE r.id > %s
        ORDER BY r.id
        LIMIT %s
    """, (last_id, BATCH))

    rows = source_cursor.fetchall()

    if not rows:
        break

    insert_data = []

    dest_cursor.execute("SELECT id FROM tickets")
    valid_tickets = set([row[0] for row in dest_cursor.fetchall()])

    for r in rows:

        if r["ticket_id"] not in valid_tickets:
            last_id = r["id"]
            continue

        # INBOUND
        if r["user_id"] == 0:
            direction = "inbound"
            from_email = r["email_id"] or r["customer_email"] or "unknown@unknown.com"
            to_email = "info@reginaldmen.com"
            created_by = None

        # OUTBOUND
        else:
            direction = "outbound"
            from_email = "info@reginaldmen.com"
            to_email = r["customer_email"] or "unknown@unknown.com"
            created_by = r["user_id"]

        insert_data.append((
            r["id"],
            r["ticket_id"],
            direction,
            from_email,
            to_email,
            r["subject"],
            r["body"],
            None,
            None,
            None,
            r["created_at"],
            created_by
        ))

        last_id = r["id"]

    insert_query = """
    INSERT IGNORE INTO ticket_messages
    (
        id,
        ticket_id,
        direction,
        from_email,
        to_email,
        subject,
        body,
        attachments_json,
        smtp_message_id,
        in_reply_to,
        sent_at,
        created_by
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    dest_cursor.executemany(insert_query, insert_data)
    dest_conn.commit()

    total += len(insert_data)
    print(f"Migrated replies: {total}")

print("Replies migration completed")

source_cursor.close()
dest_cursor.close()
source_conn.close()
dest_conn.close()