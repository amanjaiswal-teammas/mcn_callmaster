from fastapi import APIRouter, Request, HTTPException
import mysql.connector

DB_CONFIG = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "dialer_db",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


router = APIRouter(prefix="/api/webhook", tags=["CDR Webhook"])


@router.post("/cdr/bla-bli-blu")
async def save_cdr(request: Request):
    data = await request.json()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO cdr_bla_bli_blu (
            client_id,
            date_time,
            call_uuid,
            customer_name,
            customer_number,
            contact_unique_id,
            did_clid,
            created_on,
            campaign_name,
            queue_name,
            list_name,
            call_direction,
            call_status,
            agent_name,
            agent_username,
            agent_number,
            abandoned_on_agents,
            customer_call_setup_time,
            duration,
            total_call_duration,
            wrapup_time,
            total_hold_time,
            hold_time_detail,
            total_mute_time,
            mute_time_detail,
            agent_ringing_time,
            hangup_cause,
            hangup_cause_code,
            call_type,
            disposition,
            sub_disposition_1,
            sub_disposition_2,
            sub_disposition_3,
            sub_disposition_4,
            sub_disposition_5,
            call_back_disposition,
            custom_field_data,
            remark,
            recording,
            disconnected_by,
            queue_wait_time,
            dtmfs
        )
        VALUES (
            487,
            %(date_time)s,
            %(call_uuid)s,
            %(customer_name)s,
            %(customer_number)s,
            %(contact_unique_id)s,
            %(did_clid)s,
            %(created_on)s,
            %(campaign_name)s,
            %(queue_name)s,
            %(list_name)s,
            %(call_direction)s,
            %(call_status)s,
            %(agent_name)s,
            %(agent_username)s,
            %(agent_number)s,
            %(abandoned_on_agents)s,
            %(customer_call_setup_time)s,
            %(duration)s,
            %(total_call_duration)s,
            %(wrapup_time)s,
            %(total_hold_time)s,
            %(hold_time_detail)s,
            %(total_mute_time)s,
            %(mute_time_detail)s,
            %(agent_ringing_time)s,
            %(hangup_cause)s,
            %(hangup_cause_code)s,
            %(call_type)s,
            %(disposition)s,
            %(sub_disposition_1)s,
            %(sub_disposition_2)s,
            %(sub_disposition_3)s,
            %(sub_disposition_4)s,
            %(sub_disposition_5)s,
            %(call_back_disposition)s,
            %(custom_field_data)s,
            %(remark)s,
            %(recording)s,
            %(disconnected_by)s,
            %(queue_wait_time)s,
            %(dtmfs)s
        )
        """

        cursor.execute(query, data)

        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/apr/bla-bli-blu")
async def save_apr(request: Request):
    data = await request.json()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO apr_bla_bli_blu (
            client_id,
            date_time,
            agent_name,
            agent_username,
            campaigns,
            first_login_time,
            last_logout_time,
            login_duration,
            net_login_duration,
            idle_waiting_duration,
            auto_call_off,
            total_talktime,
            total_hold_time,
            total_wrapup_time,
            total_handling_time,
            average_talk_time,
            average_hold_time,
            average_wrapup_time,
            average_handling_time,
            lunch_break_duration,
            meeting_break_duration,
            tea_break_duration,
            training_break_duration,
            wb_break_duration,
            total_break_time
        )
        VALUES (
            487,
            %(date_time)s,
            %(agent_name)s,
            %(agent_username)s,
            %(campaigns)s,
            %(first_login_time)s,
            %(last_logout_time)s,
            %(login_duration)s,
            %(net_login_duration)s,
            %(idle_waiting_duration)s,
            %(auto_call_off)s,
            %(total_talktime)s,
            %(total_hold_time)s,
            %(total_wrapup_time)s,
            %(total_handling_time)s,
            %(average_talk_time)s,
            %(average_hold_time)s,
            %(average_wrapup_time)s,
            %(average_handling_time)s,
            %(lunch_break_duration)s,
            %(meeting_break_duration)s,
            %(tea_break_duration)s,
            %(training_break_duration)s,
            %(wb_break_duration)s,
            %(total_break_time)s
        )
        """

        cursor.execute(query, data)

        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "APR saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
