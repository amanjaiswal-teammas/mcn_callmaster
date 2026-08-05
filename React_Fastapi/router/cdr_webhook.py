from fastapi import APIRouter, Request, HTTPException
import mysql.connector
import json

DB_CONFIG = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "dialer_db",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


router = APIRouter(prefix="/api/webhook", tags=["CDR Webhook"])


# @router.post("/cdr/bla-bli-blu")
# async def save_cdr(request: Request):
#     data = await request.json()
#
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#
#         query = """
#         INSERT INTO cdr_bla_bli_blu (
#             client_id,
#             date_time,
#             call_uuid,
#             customer_name,
#             customer_number,
#             contact_unique_id,
#             did_clid,
#             created_on,
#             campaign_name,
#             queue_name,
#             list_name,
#             call_direction,
#             call_status,
#             agent_name,
#             agent_username,
#             agent_number,
#             abandoned_on_agents,
#             customer_call_setup_time,
#             duration,
#             total_call_duration,
#             wrapup_time,
#             total_hold_time,
#             hold_time_detail,
#             total_mute_time,
#             mute_time_detail,
#             agent_ringing_time,
#             hangup_cause,
#             hangup_cause_code,
#             call_type,
#             disposition,
#             sub_disposition_1,
#             sub_disposition_2,
#             sub_disposition_3,
#             sub_disposition_4,
#             sub_disposition_5,
#             call_back_disposition,
#             custom_field_data,
#             remark,
#             recording,
#             disconnected_by,
#             queue_wait_time,
#             dtmfs
#         )
#         VALUES (
#             487,
#             %(date_time)s,
#             %(call_uuid)s,
#             %(customer_name)s,
#             %(customer_number)s,
#             %(contact_unique_id)s,
#             %(did_clid)s,
#             %(created_on)s,
#             %(campaign_name)s,
#             %(queue_name)s,
#             %(list_name)s,
#             %(call_direction)s,
#             %(call_status)s,
#             %(agent_name)s,
#             %(agent_username)s,
#             %(agent_number)s,
#             %(abandoned_on_agents)s,
#             %(customer_call_setup_time)s,
#             %(duration)s,
#             %(total_call_duration)s,
#             %(wrapup_time)s,
#             %(total_hold_time)s,
#             %(hold_time_detail)s,
#             %(total_mute_time)s,
#             %(mute_time_detail)s,
#             %(agent_ringing_time)s,
#             %(hangup_cause)s,
#             %(hangup_cause_code)s,
#             %(call_type)s,
#             %(disposition)s,
#             %(sub_disposition_1)s,
#             %(sub_disposition_2)s,
#             %(sub_disposition_3)s,
#             %(sub_disposition_4)s,
#             %(sub_disposition_5)s,
#             %(call_back_disposition)s,
#             %(custom_field_data)s,
#             %(remark)s,
#             %(recording)s,
#             %(disconnected_by)s,
#             %(queue_wait_time)s,
#             %(dtmfs)s
#         )
#         """
#
#         cursor.execute(query, data)
#
#         conn.commit()
#         cursor.close()
#         conn.close()
#
#         return {"status": "success"}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/cdr/bla-bli-blu")
async def save_cdr(request: Request):
    body = await request.json()

    call = body.get("call_details", {})
    customer = body.get("customer_details", {})
    agents = body.get("agent_details", [])

    agent = agents[0] if agents else {}

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
            did_clid,
            created_on,
            queue_name,
            call_direction,
            call_status,
            agent_name,
            agent_username,
            agent_number,
            duration,
            total_call_duration,
            recording,
            remark,
            disconnected_by,

            sme_id,
            ringing_duration,
            ivr_duration,
            overall_call_status,
            talk_time,
            flow_name,
            end_date_time,
            call_recording_status,
            customer_hangup_cause,
            customer_number_without_countrycode,
            agent_id,
            call_route_reason,
            agent_number_without_countrycode,
            agent_email,
            custom_params
        )
        VALUES (
            487,
            %(date_time)s,
            %(call_uuid)s,
            %(customer_name)s,
            %(customer_number)s,
            %(did_clid)s,
            %(created_on)s,
            %(queue_name)s,
            %(call_direction)s,
            %(call_status)s,
            %(agent_name)s,
            %(agent_username)s,
            %(agent_number)s,
            %(duration)s,
            %(total_call_duration)s,
            %(recording)s,
            %(remark)s,
            %(disconnected_by)s,

            %(sme_id)s,
            %(ringing_duration)s,
            %(ivr_duration)s,
            %(overall_call_status)s,
            %(talk_time)s,
            %(flow_name)s,
            %(end_date_time)s,
            %(call_recording_status)s,
            %(customer_hangup_cause)s,
            %(customer_number_without_countrycode)s,
            %(agent_id)s,
            %(call_route_reason)s,
            %(agent_number_without_countrycode)s,
            %(agent_email)s,
            %(custom_params)s
        )
        """

        values = {
            "date_time": call.get("start_date_time"),
            "call_uuid": call.get("session_id"),
            "customer_name": customer.get("customer_name"),
            "customer_number": customer.get("customer_number"),
            "did_clid": call.get("longcode"),
            "created_on": call.get("start_date_time"),
            "queue_name": call.get("queue_name"),
            "call_direction": call.get("call_direction"),
            "call_status": customer.get("call_status"),
            "agent_name": agent.get("agent_name"),
            "agent_username": agent.get("agent_email"),
            "agent_number": agent.get("agent_mobile"),
            "duration": call.get("connected_duration"),
            "total_call_duration": call.get("duration"),
            "recording": call.get("recording_url"),
            "remark": call.get("remarks"),
            "disconnected_by": call.get("disconnected_by"),

            "sme_id": call.get("sme_id"),
            "ringing_duration": call.get("ringing_duration"),
            "ivr_duration": call.get("ivr_duration"),
            "overall_call_status": call.get("overall_call_status"),
            "talk_time": call.get("talkTime"),
            "flow_name": call.get("flow_name"),
            "end_date_time": call.get("end_date_time"),
            "call_recording_status": call.get("call_recording_status"),
            "customer_hangup_cause": customer.get("customer_hangup_cause"),
            "customer_number_without_countrycode": customer.get("customer_number_without_countryCode"),
            "agent_id": agent.get("agent_id"),
            "call_route_reason": agent.get("call_route_reason"),
            "agent_number_without_countrycode": agent.get("agent_number_without_countryCode"),
            "agent_email": agent.get("agent_email"),
            "custom_params": json.dumps(call.get("custom_params"))
            if call.get("custom_params") is not None
            else None,
        }

        cursor.execute(query, values)

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "message": "CDR saved successfully."
        }

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





@router.post("/cdr/finnable")
async def save_finnable_call_log(request: Request):
    data = await request.json()

    try:
        duration = int(data.get("duration", 0))

        # Skip calls less than 120 sec
        if duration < 120:
            return {
                "status": "skipped",
                "message": "Duration less than 120 seconds"
            }

        conn = get_connection()
        cursor = conn.cursor()

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

        insert_data = {
            "lead_id": data.get("lead_id"),
            "call_id": data.get("call_id"),
            "agent_id": data.get("agent_id"),
            "start_time": data.get("start_time"),
            "end_time": data.get("end_time"),
            "duration": duration,
            "recording_path": data.get("recording_path", ""),
        }

        cursor.execute(query, insert_data)

        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success"}

    except mysql.connector.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Duplicate entry for client_id + lead_id + start_time"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))