from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from sqlalchemy import create_engine, text
import json
from collections import Counter
from datetime import datetime
from collections import OrderedDict
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/dashboard3")

# Database connection
engine = create_engine("mysql+pymysql://root:321%2A%23LDtr%21%3F%2Aktasb@192.168.10.22/db_dialdesk")


class FilterParams(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    agent_name: Optional[str] = None
    team: Optional[str] = None
    region: Optional[str] = None
    campaign: Optional[str] = None
    min_confidence_score: Optional[int] = None
    disposition: Optional[str] = None  # "PTP Given" or "Not Given"


@router.post("/summary")
def get_summary(filters: FilterParams):
    today = date.today()
    query = """
        SELECT
            COUNT(*) AS total_ptps,
            SUM(CASE WHEN ptp_confidence_score < 60 THEN 1 ELSE 0 END) AS low_confidence,
            SUM(CASE WHEN ptp_confidence_score >= 60 THEN 1 ELSE 0 END) AS high_confidence,
            SUM(CASE WHEN predicted_to_fail = 1 THEN 1 ELSE 0 END) AS ptps_failed,
            SUM(CASE WHEN follow_up_needed = 1 THEN 1 ELSE 0 END) AS follow_up_cases
        FROM tbl_collection
        WHERE 1=1
    """
    conditions = []
    params = {}

    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params['start_date'] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params['end_date'] = filters.end_date

    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params['agent_name'] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params['team'] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params['region'] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params['campaign'] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    # print(query)
    with engine.connect() as conn:
        result = conn.execute(text(query), params).fetchone()

    return {
        "total_ptps": result[0],
        "low_confidence": result[1],
        "high_confidence": result[2],
        "ptps_failed": result[3],
        "follow_up_cases": result[4],
    }



@router.post("/ptp-distribution")
def ptp_confidence_distribution(filters: FilterParams):
    today = date.today()

    query = """
        SELECT 
        FLOOR(ptp_confidence_score / 10) * 10 AS score_range,
        COUNT(*) as count
    FROM tbl_collection
    WHERE ptp_confidence_score IS NOT NULL
    """
    conditions = []
    params = {}

    # 🔹 Default to today's date if not provided
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params['start_date'] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params['end_date'] = filters.end_date

    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params['agent_name'] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params['team'] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params['region'] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params['campaign'] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY score_range ORDER BY score_range"

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    return [
        {
            "range_label": f"{int(row[0])}-{int(row[0]) + 9}",
            "count": row[1]
        }
        for row in results
    ]


@router.post("/sentiment-pie-distribution")
def sentiment_pie_distribution(filters: FilterParams):
    today = date.today()

    query = """
        SELECT hesitation_markers, confident_phrases
        FROM tbl_collection
        WHERE (hesitation_markers IS NOT NULL OR confident_phrases IS NOT NULL)
    """
    conditions = []
    params = {}

    # 📅 Default to today if no date filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params['start_date'] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params['end_date'] = filters.end_date

    # 🧍‍♂️ Optional filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params['agent_name'] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params['team'] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params['region'] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params['campaign'] = filters.campaign.strip()

    # Append conditions to query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Query DB
    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    hesitation_counter = Counter()
    confident_counter = Counter()

    # Count phrases
    for row in results:
        hesitations = json.loads(row[0] or "[]")
        confidents = json.loads(row[1] or "[]")

        hesitation_counter.update(hesitations)
        confident_counter.update(confidents)

    # Format output for single pie chart
    output = []

    for phrase, count in hesitation_counter.items():
        output.append({
            "phrase": phrase,
            "count": count,
            "category": "Hesitation"
        })

    for phrase, count in confident_counter.items():
        output.append({
            "phrase": phrase,
            "count": count,
            "category": "Confident"
        })

    return output


@router.post("/ptp-insights-detailed")
def ptp_insights_detailed(filters: FilterParams):
    today = date.today()

    query = """
        SELECT 
            DATE(call_time) AS call_date,
            agent_name,
            customer_name,
            sentiment,
            confidence_score
        FROM tbl_collection
        WHERE sentiment IS NOT NULL AND confidence_score IS NOT NULL
    """
    conditions = []
    params = {}

    # 📅 Date Filtering
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params['start_date'] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params['end_date'] = filters.end_date

    # 🧍‍♀️ Other Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params['agent_name'] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params['team'] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params['region'] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params['campaign'] = filters.campaign.strip()

    # Apply conditions
    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " ORDER BY call_time DESC"

    # Fetch and format data
    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    return [
        {
            "date": row[0].strftime("%d %b"),  # e.g., "25 Apr"
            "agent": row[1],
            "customer_name": row[2],
            "sentiment": row[3],
            "confidence": f"{int(row[4])}%" if row[4] is not None else "N/A"
        }
        for row in results
    ]


"""
@router.post("/ptp-agent-accuracy")
def ptp_agent_accuracy(filters: FilterParams):
    today = date.today()

    query = 
        SELECT 
            agent_name,
            COUNT(*) AS total_ptps,
            ROUND(AVG(confidence_score), 0) AS avg_accuracy,
            SUM(predicted_to_fail = 1) AS failed_ptps,
            ROUND(AVG(agent_voice_score), 0) AS avg_voice_score
        FROM tbl_collection
        WHERE confidence_score IS NOT NULL
          AND agent_name IS NOT NULL

    conditions = []
    params = {}

    # 📅 Date Filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params['start_date'] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params['end_date'] = filters.end_date

    # 🔍 Additional Filters
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params['team'] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params['region'] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params['campaign'] = filters.campaign.strip()

    # Append conditions
    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY agent_name ORDER BY total_ptps DESC"

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    return [
        {
            "agent": row[0],
            "total_ptps": row[1],
            "avg_accuracy": f"{int(row[2])}%",
            "failed_ptps": row[3],
            "av%": f"{int(row[4])}%" if row[4] is not None else "N/A"
        }
        for row in results
    ]"""


@router.post("/agent-wise-accuracy")
def agent_wise_accuracy(filters: FilterParams):
    today = date.today()

    query = """
        SELECT 
            agent_name,
            COUNT(*) AS total_ptps,
            ROUND(AVG(confidence_score), 2) AS avg_confidence,
            SUM(predicted_to_fail = 1) AS failed_ptps,
            ROUND((1 - SUM(predicted_to_fail = 1) / COUNT(*)) * 100, 2) AS accuracy_pct
        FROM tbl_collection
        WHERE agent_name IS NOT NULL
          AND confidence_score IS NOT NULL
    """

    conditions = []
    params = {}

    # 🔹 Date filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params['start_date'] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params['end_date'] = filters.end_date

    # 🔹 Other filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params['agent_name'] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params['team'] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params['region'] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params['campaign'] = filters.campaign.strip()

    # 🔹 Add conditions to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY agent_name ORDER BY total_ptps DESC"

    # 🔹 Execute the query
    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    # 🔹 Format and return the result
    return [
        {
            "agent": row[0],
            "total_ptps": row[1],
            "avg_confidence": row[2],
            "failed_ptps": row[3],
            "accuracy_pct": row[4]
        }
        for row in results
    ]


@router.post("/ptp-table")
def ptp_detailed_table():
    query = """
        SELECT
            date,
            agent_name,
            customer_name,
            sentiment,
            ptp_phrase,
            confidence_score,
            predicted_to_fail,
            remarks
        FROM tbl_collection
        ORDER BY date DESC
        LIMIT 100
    """
    with engine.connect() as conn:
        results = conn.execute(text(query)).fetchall()
    return [
        {
            "date": str(row[0]),
            "agent": row[1],
            "customer_name": row[2],
            "sentiment": row[3],
            "ptp_phrase": row[4],
            "confidence": f"{row[5]}%",
            "predicted_to_fail": bool(row[6]),
            "remarks": row[7]
        } for row in results
    ]


@router.post("/follow-up-list")
def follow_up_priority():
    query = """
        SELECT
            id,
            customer_name,
            ptp_phrase,
            confidence_score,
            predicted_to_fail
        FROM tbl_collection
        WHERE follow_up_needed = 1
        ORDER BY confidence_score ASC
        LIMIT 100
    """
    with engine.connect() as conn:
        results = conn.execute(text(query)).fetchall()
    return [
        {
            "id": row[0],
            "customer_name": row[1],
            "ptp_phrase": row[2],
            "confidence_score": row[3],
            "predicted_to_fail": bool(row[4]),
            "actions": ["Schedule Call", "Mark as Paid", "Send Reminder SMS"]
        } for row in results
    ]


@router.post("/ptp-sentiment-distribution")
def ptp_sentiment_distribution(filters: FilterParams):
    from datetime import date
    today = date.today()

    query = """
        SELECT 
            sentiment,
            COUNT(*) AS count
        FROM tbl_collection
        WHERE sentiment IS NOT NULL
    """

    conditions = []
    params = {}

    # 🔹 Date Filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # 🔹 Additional Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY sentiment"

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    # 🔹 Response format for pie chart
    return [
        {
            "sentiment": row[0],
            "count": row[1]
        }
        for row in results
    ]


@router.post("/ptp-intent-classification")
def ptp_intent_classification(filters: FilterParams):
    today = date.today()

    query = """
        SELECT intent_classification
        FROM tbl_collection
        WHERE intent_classification IS NOT NULL
    """
    conditions = []
    params = {}

    # 🔹 Date Filter Defaults
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # 🔹 Optional Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    with engine.connect() as conn:
        result = conn.execute(text(query), params).fetchall()

    # 🔹 Initialize counters
    classification_counts = {
        "Willing but Delayed": 0,
        "Unwilling": 0,
        "Can't Pay": 0
    }

    for row in result:
        try:
            intent_json = json.loads(row[0])
            if intent_json.get("willing_but_delayed"):
                classification_counts["Willing but Delayed"] += 1
            elif intent_json.get("unwilling"):
                classification_counts["Unwilling"] += 1
            elif intent_json.get("cant_pay"):
                classification_counts["Can't Pay"] += 1
        except Exception:
            continue  # skip malformed rows

    return [
        {"intent": k, "count": v} for k, v in classification_counts.items()
    ]


@router.post("/ptp-root-cause-detection")
def ptp_root_cause_detection(filters: FilterParams):
    today = date.today()

    query = """
        SELECT root_cause
        FROM tbl_collection
        WHERE root_cause IS NOT NULL
    """
    conditions = []
    params = {}

    # 🔹 Date Filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # 🔹 Optional Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    # 🔍 Mapping logic
    def classify(text):
        text = text.lower()
        if "job" in text or "unemploy" in text:
            return "Job Loss"
        elif "cash" in text or "salary" in text or "income" in text:
            return "Cash Flow Issues"
        elif "dispute" in text or "argument" in text:
            return "Dispute"
        else:
            return "Other"

    root_cause_counter = Counter()

    for row in results:
        try:
            causes = json.loads(row[0])
            if isinstance(causes, list):
                for cause in causes:
                    label = classify(cause)
                    root_cause_counter[label] += 1
            else:
                root_cause_counter[classify(str(causes))] += 1
        except Exception:
            root_cause_counter["Other"] += 1

    total = sum(root_cause_counter.values())
    return [
        {
            "root_cause": cause,
            "count": count,
            "percentage": round((count / total) * 100, 2)
        }
        for cause, count in root_cause_counter.items()
    ]


@router.post("/ptp-agent-forced-by-weekday")
def ptp_agent_forced_by_weekday(filters: FilterParams):
    today = date.today()

    query = """
        SELECT 
            DAYNAME(call_time) as weekday,
            COUNT(*) as count
        FROM tbl_collection
        WHERE agent_forced_ptp_detected = 1
    """

    conditions = []
    params = {}

    # 🔹 Default to today if no range
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # 🔹 Optional filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY DAYOFWEEK(call_time), DAYNAME(call_time)"

    weekday_map = {
        "Sunday": 0, "Monday": 1, "Tuesday": 2,
        "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6
    }

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    # Normalize results to fixed weekday order
    data = {day: 0 for day in weekday_map.keys()}
    for row in results:
        weekday = row[0]
        count = row[1]
        if weekday in data:
            data[weekday] = count

    # Return in sorted weekday order
    sorted_result = [
        {"day": day, "forced_ptps": data[day]}
        for day in sorted(data, key=lambda d: weekday_map[d])
    ]

    return sorted_result


@router.post("/escalation-risk-alerts")
def escalation_risk_alerts(filters: FilterParams):
    today = date.today()

    query = """
        SELECT escalation_risks
        FROM tbl_collection
        WHERE escalation_risks IS NOT NULL
    """
    conditions = []
    params = {}

    # Date filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # Optional filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    # List of tracked escalation phrases
    tracked_phrases = [
        "I'll complain",
        "going to consumer court",
        "social media"
    ]

    phrase_counter = Counter()
    total_records = len(results)

    for row in results:
        try:
            # Assume escalation_risks column stores JSON array of strings
            risks = json.loads(row[0])
            if isinstance(risks, list):
                for risk in risks:
                    if risk in tracked_phrases:
                        phrase_counter[risk] += 1
        except Exception:
            continue

    return [
        {
            "phrase": phrase,
            "count": phrase_counter.get(phrase, 0),
            "percentage": round((phrase_counter.get(phrase, 0) / total_records) * 100, 2) if total_records > 0 else 0.0
        }
        for phrase in tracked_phrases
    ]


@router.post("/dispute-management")
def dispute_management(filters: FilterParams):
    today = date.today()

    query = """
        SELECT dispute_management
        FROM tbl_collection
        WHERE dispute_management IS NOT NULL
    """
    conditions = []
    params = {}

    # Date filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # Optional filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    total_dispute_percentage = 0
    reason_counter = Counter()
    record_count = 0

    for row in results:
        try:
            dispute_data = json.loads(row[0])
            total_dispute_percentage += dispute_data.get("dispute_percentage", 0)
            reasons = dispute_data.get("reasons", [])
            if isinstance(reasons, list):
                for r in reasons:
                    reason_counter[r] += 1
            record_count += 1
        except Exception:
            continue

    avg_dispute_percentage = round((total_dispute_percentage / record_count), 2) if record_count > 0 else 0

    # Known dispute reasons to keep order and filter
    known_reasons = [
        "I've already paid",
        "Wrong charges",
        "False promises",
        "Reversal pending",
        "Not my account"
    ]

    return {
        "dispute_percentage": avg_dispute_percentage,
        "reasons": [
            {"reason": reason, "count": reason_counter.get(reason, 0)}
            for reason in known_reasons if reason_counter.get(reason, 0) > 0
        ]
    }


@router.post("/agent-behavior-monitoring")
def agent_behavior_monitoring(filters: FilterParams):
    today = date.today()

    query = """
        SELECT agent_behavior
        FROM tbl_collection
        WHERE agent_behavior IS NOT NULL
    """
    conditions = []
    params = {}

    # Date Filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # Optional Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    behavior_counter = Counter({
        "harsh_tone": 0,
        "abusive_language": 0,
        "false_promises": 0,
        "threatening_tone": 0
    })

    total = 0
    for row in results:
        try:
            behavior = json.loads(row[0])
            if behavior.get("harsh_tone"):
                behavior_counter["harsh_tone"] += 1
            if behavior.get("abusive_language"):
                behavior_counter["abusive_language"] += 1
            if behavior.get("false_promises"):
                behavior_counter["false_promises"] += 1
            if behavior.get("threatening_tone"):
                behavior_counter["threatening_tone"] += 1
            total += 1
        except Exception:
            pass

    if total == 0:
        return []

    return [
        {
            "behavior": "Harsh Tone",
            "count": behavior_counter["harsh_tone"],
            "percentage": round((behavior_counter["harsh_tone"] / total) * 100, 2)
        },
        {
            "behavior": "Abusive Language",
            "count": behavior_counter["abusive_language"],
            "percentage": round((behavior_counter["abusive_language"] / total) * 100, 2)
        },
        {
            "behavior": "False Promises",
            "count": behavior_counter["false_promises"],
            "percentage": round((behavior_counter["false_promises"] / total) * 100, 2)
        },
        {
            "behavior": "Threatening Tone",
            "count": behavior_counter["threatening_tone"],
            "percentage": round((behavior_counter["threatening_tone"] / total) * 100, 2)
        }
    ]


@router.post("/emotional-sentiment-analysis")
def emotional_sentiment_analysis(filters: FilterParams):
    today = date.today()

    query = """
        SELECT emotional_sentiment
        FROM tbl_collection
        WHERE emotional_sentiment IS NOT NULL
    """
    conditions = []
    params = {}

    # Date Filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # Optional Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    # Counters for dominant emotions and timeline trends
    dominant_counter = Counter()
    timeline_counter = Counter()
    total = 0

    for row in results:
        try:
            data = json.loads(row[0])
            dominant = data.get("dominant_emotion", "Unknown")
            timeline = data.get("timeline_trend", [])

            dominant_counter[dominant] += 1
            timeline_counter.update(timeline)
            total += 1
        except Exception:
            pass

    if total == 0:
        return []

    return {
        "dominant_emotion_distribution": [
            {"emotion": emotion, "count": count, "percentage": round((count / total) * 100, 2)}
            for emotion, count in dominant_counter.items()
        ],
        "timeline_trend_distribution": [
            {"emotion": emotion, "count": count, "percentage": round((count / sum(timeline_counter.values())) * 100, 2)}
            for emotion, count in timeline_counter.items()
        ]
    }


@router.post("/collection-funnel-optimization")
def collection_funnel_optimization(filters: FilterParams):
    today = date.today()

    query = """
        SELECT collection_funnel
        FROM tbl_collection
        WHERE collection_funnel IS NOT NULL
    """
    conditions = []
    params = {}

    # Date filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # Optional filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    # Count repayment barrier levels
    barrier_counts = {"low": 0, "medium": 0, "high": 0}
    total = 0
    for row in results:
        level = str(row[0]).lower()
        if level in barrier_counts:
            barrier_counts[level] += 1
            total += 1

    # If no data, return default/fallback
    if total == 0:
        total = 1  # avoid div by zero

    # Calculate percentages (example mapping stages arbitrarily)
    stages = [
        {"name": "Stage 1", "value": 25, "barrier": "low"},
        {"name": "Stage 2", "value": 50, "barrier": "medium"},
        {"name": "Stage 3", "value": 75, "barrier": "high"},
        {"name": "Stage 4", "value": 100, "barrier": "low"},
    ]

    response = {
        "title": "Collection Funnel Optimization",
        "stages": stages,
        "repaymentBarriers": {
            "low": "Low",
            "high": "High"
        },
        "counts": barrier_counts,
        "total_records": total
    }
    return response


@router.post("/ptp-summary-stats")
def ptp_summary_stats(filters: FilterParams):
    today = date.today()

    query = """
        SELECT 
            COUNT(*) AS total_calls,
            SUM(call_disposition = 'PTP Given') AS ptp_count,
            SUM(call_disposition = 'PTP Given' AND predicted_to_fail = 0) AS rtp_count,
            SUM(CASE WHEN call_disposition = 'PTP Given' THEN ptp_amount ELSE 0 END) AS ptp_amount_total,
            SUM(CASE WHEN call_disposition = 'PTP Given' AND predicted_to_fail = 0 THEN ptp_amount ELSE 0 END) AS rtp_amount_total
        FROM tbl_collection
        WHERE 1 = 1
    """
    conditions = []
    params = {}

    # Date Filters
    if not filters.start_date and not filters.end_date:
        conditions.append("DATE(call_time) = :today")
        params["today"] = today
    else:
        if filters.start_date:
            conditions.append("DATE(call_time) >= :start_date")
            params["start_date"] = filters.start_date
        if filters.end_date:
            conditions.append("DATE(call_time) <= :end_date")
            params["end_date"] = filters.end_date

    # Optional Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    with engine.connect() as conn:
        result = conn.execute(text(query), params).mappings().first()

    return {
        "total_calls": result["total_calls"] or 0,
        "ptp_count": result["ptp_count"] or 0,
        "rtp_count": result["rtp_count"] or 0,
        "ptp_amount": float(result["ptp_amount_total"] or 0),
        "rtp_amount": float(result["rtp_amount_total"] or 0),
        "not_given_count": (result["total_calls"] or 0) - (result["ptp_count"] or 0)
    }


@router.post("/ptp-rtp-monthly-trends")
def ptp_rtp_monthly_trends(filters: FilterParams):
    query = """
        SELECT 
            DATE_FORMAT(call_time, '%Y-%m') AS month,
            SUM(CASE WHEN call_disposition = 'PTP Given' THEN ptp_amount ELSE 0 END) AS ptp_amount,
            SUM(CASE WHEN call_disposition = 'PTP Given' AND predicted_to_fail = 0 THEN ptp_amount ELSE 0 END) AS rtp_amount
        FROM tbl_collection
        WHERE call_time IS NOT NULL
    """
    conditions = []
    params = {}

    # Date Filters
    if filters.start_date:
        conditions.append("DATE(call_time) >= :start_date")
        params["start_date"] = filters.start_date
    if filters.end_date:
        conditions.append("DATE(call_time) <= :end_date")
        params["end_date"] = filters.end_date
    else:
        from datetime import date
        current_year = date.today().year
        conditions.append("YEAR(call_time) = :year")
        params["year"] = current_year

    # Optional Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY month ORDER BY month"

    # Month labels
    all_months = OrderedDict((datetime(1900, m, 1).strftime('%b'), {'PTP': 0, 'RTP': 0}) for m in range(1, 13))

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    # Fill actual data into the default months
    for row in results:
        month_str = datetime.strptime(row[0], "%Y-%m").strftime('%b')  # 'Jan', 'Feb', etc.
        if month_str in all_months:
            all_months[month_str]['PTP'] = float(row[1] or 0)
            all_months[month_str]['RTP'] = float(row[2] or 0)

    # Final structured data for frontend
    return [
        {"month": month, "PTP": data["PTP"], "RTP": data["RTP"]}
        for month, data in all_months.items()
    ]


@router.post("/ptp-by-agent")
def ptp_by_agent(filters: FilterParams):
    query = """
        SELECT agent_name, SUM(ptp_amount) AS total_ptp
        FROM tbl_collection
        WHERE call_disposition = 'PTP Given' AND ptp_amount IS NOT NULL
    """
    conditions = []
    params = {}

    # Date Filters
    if filters.start_date:
        conditions.append("DATE(call_time) >= :start_date")
        params["start_date"] = filters.start_date
    if filters.end_date:
        conditions.append("DATE(call_time) <= :end_date")
        params["end_date"] = filters.end_date

    # Optional Filters
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY agent_name ORDER BY total_ptp DESC"

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    return {
        "agents": [row[0] for row in results],
        "ptp_amounts": [float(row[1]) for row in results]
    }


@router.post("/ptp-fulfillment-table")
def ptp_fulfillment_table(filters: FilterParams):
    query = """
        SELECT
            customer_num AS customer_id,
            agent_name,
            DATE(call_time) AS call_date,
            ptp_amount,
            predicted_to_fail
        FROM tbl_collection
        WHERE call_disposition = 'PTP Given' AND ptp_amount IS NOT NULL
    """
    conditions = []
    params = {}

    # Date Filters
    if filters.start_date:
        conditions.append("DATE(call_time) >= :start_date")
        params["start_date"] = filters.start_date
    if filters.end_date:
        conditions.append("DATE(call_time) <= :end_date")
        params["end_date"] = filters.end_date

    # Optional Filters
    if filters.agent_name and filters.agent_name.strip().lower() != "string":
        conditions.append("agent_name = :agent_name")
        params["agent_name"] = filters.agent_name.strip()
    if filters.team and filters.team.strip().lower() != "string":
        conditions.append("team = :team")
        params["team"] = filters.team.strip()
    if filters.region and filters.region.strip().lower() != "string":
        conditions.append("region = :region")
        params["region"] = filters.region.strip()
    if filters.campaign and filters.campaign.strip().lower() != "string":
        conditions.append("campaign = :campaign")
        params["campaign"] = filters.campaign.strip()

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " ORDER BY call_time DESC"

    with engine.connect() as conn:
        results = conn.execute(text(query), params).fetchall()

    data = []
    for row in results:
        status = "Fulfilled" if not row[4] else "Pending"
        data.append({
            "customer_id": row[0],
            "agent": row[1],
            "call_date": str(row[2]),
            "promised_amount": float(row[3]),
            "status": status
        })

    return {"data": data}




@router.get("/latest-transcribe-audit")
async def get_latest_transcribe_and_audit(agent_no: str = Query(...), leadid: str = Query(...)):
    query = """
        SELECT transcribe_text, analysis_json
        FROM tbl_collection
        WHERE agent_no = :agent_no
        AND leadid = :leadid
        ORDER BY call_time DESC
        LIMIT 1
    """
    print(query)
    with engine.connect() as conn:
        result = conn.execute(text(query), {"agent_no": agent_no, "leadid": leadid}).fetchone()

    if not result:
        return JSONResponse(
            content={"status": "error", "message": "No matching call found"},
            status_code=404
        )

    transcribe_text, analysis_json = result
    try:
        audit_data = json.loads(analysis_json) if analysis_json else {}
    except json.JSONDecodeError:
        audit_data = {"error": "Invalid audit JSON"}

    return {
        "status": "success",
        "agent_no": agent_no,
        "leadid": leadid,
        "transcribe": transcribe_text or "",
        "audit": audit_data
    }

