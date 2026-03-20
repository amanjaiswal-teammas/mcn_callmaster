from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional

# DB Configuration
DATABASE_URL = "mysql+pymysql://root:dial%40mas123@192.168.11.6/db_dialdesk"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter(prefix="/api/call-master", tags=["CallMaster Settings"])


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API to fetch companies + agents
@router.get("/active-data")
def get_active_data(db: Session = Depends(get_db)):
    # Query for companies
    company_query = text("""
        SELECT company_id, company_name
        FROM registration_master
        WHERE status = 'A'
    """)

    # Query for agents
    agent_query = text("""
        SELECT username, displayname, ClientRights
        FROM agent_master
        WHERE status = 'A'
    """)

    companies = db.execute(company_query).fetchall()
    agents = db.execute(agent_query).fetchall()

    result = []

    for c in companies:
        company_id_str = str(c.company_id)

        mapped_agents = []

        for a in agents:
            if a.ClientRights:
                rights = [r.strip() for r in a.ClientRights.split(",")]

                if company_id_str in rights:
                    mapped_agents.append({
                        "username": a.username,
                        "displayname": a.displayname
                    })

        result.append({
            "company_id": c.company_id,
            "company_name": c.company_name,
            "agents": mapped_agents
        })

    return result






class AuditConfigCreate(BaseModel):
    client_id: int
    agent_users: Optional[str] = None

    min_call_duration: int = 0
    max_call_duration: int = 0

    audit_call_count_per_agent: int = 0

    time_from: str
    time_to: str

    call_type: str

    total_audit_call_count: int = 0
    dialer_server_ip: str


class AuditConfigUpdate(AuditConfigCreate):
    pass



def get_agent_count(agent_users: str) -> int:
    if not agent_users:
        return 0
    return len([a.strip() for a in agent_users.split(",") if a.strip()])


# =========================
# ✅ CREATE
# =========================

@router.post("/audit-config")
def create_audit_config(data: AuditConfigCreate, db: Session = Depends(get_db)):

    agent_count = get_agent_count(data.agent_users)

    remaining = data.total_audit_call_count - (
            data.audit_call_count_per_agent * agent_count
    )

    if remaining < 0:
        raise HTTPException(
            status_code=400,
            detail="Total audit count is less than required per agent allocation"
        )

    query = text("""
        INSERT INTO audit_config (
            client_id,
            agent_users,
            min_call_duration,
            max_call_duration,
            audit_call_count_per_agent,
            time_from,
            time_to,
            call_type,
            total_audit_call_count,
            remaining_audit_call_count,
            dialer_server_ip
        ) VALUES (
            :client_id,
            :agent_users,
            :min_call_duration,
            :max_call_duration,
            :audit_call_count_per_agent,
            :time_from,
            :time_to,
            :call_type,
            :total_audit_call_count,
            :remaining_audit_call_count,
            :dialer_server_ip
        )
    """)

    db.execute(query, {
        **data.dict(),
        "remaining_audit_call_count": remaining
    })

    db.commit()

    return {"message": "Audit config created successfully"}


# =========================
# ✅ READ (ALL)
# =========================

@router.get("/audit-config")
def get_audit_configs(db: Session = Depends(get_db)):

    query = text("""
        SELECT *
        FROM audit_config
        ORDER BY id DESC
    """)

    result = db.execute(query).fetchall()

    return [
        {
            "id": r.id,
            "client_id": r.client_id,
            "agent_users": r.agent_users,
            "min_call_duration": r.min_call_duration,
            "max_call_duration": r.max_call_duration,
            "audit_call_count_per_agent": r.audit_call_count_per_agent,
            "time_from": str(r.time_from),
            "time_to": str(r.time_to),
            "call_type": r.call_type,
            "total_audit_call_count": r.total_audit_call_count,
            "remaining_audit_call_count": r.remaining_audit_call_count,
            "dialer_server_ip": r.dialer_server_ip,
            "created_at": str(r.created_at)
        }
        for r in result
    ]


# =========================
# ✅ READ (ONE)
# =========================

@router.get("/audit-config/{config_id}")
def get_audit_config(config_id: int, db: Session = Depends(get_db)):

    query = text("""
        SELECT * FROM audit_config WHERE id = :id
    """)

    r = db.execute(query, {"id": config_id}).fetchone()

    if not r:
        raise HTTPException(status_code=404, detail="Config not found")

    return {
        "id": r.id,
        "client_id": r.client_id,
        "agent_users": r.agent_users,
        "min_call_duration": r.min_call_duration,
        "max_call_duration": r.max_call_duration,
        "audit_call_count_per_agent": r.audit_call_count_per_agent,
        "time_from": str(r.time_from),
        "time_to": str(r.time_to),
        "call_type": r.call_type,
        "total_audit_call_count": r.total_audit_call_count,
        "remaining_audit_call_count": r.remaining_audit_call_count,
        "dialer_server_ip": r.dialer_server_ip
    }


# =========================
# ✅ UPDATE
# =========================

@router.put("/audit-config/{config_id}")
def update_audit_config(
    config_id: int,
    data: AuditConfigUpdate,
    db: Session = Depends(get_db)
):

    # check exists
    check = db.execute(
        text("SELECT id FROM audit_config WHERE id = :id"),
        {"id": config_id}
    ).fetchone()

    if not check:
        raise HTTPException(status_code=404, detail="Config not found")

    agent_count = get_agent_count(data.agent_users)

    remaining = data.total_audit_call_count - (
            data.audit_call_count_per_agent * agent_count
    )

    if remaining < 0:
        raise HTTPException(
            status_code=400,
            detail="Total audit count is less than required per agent allocation"
        )

    query = text("""
        UPDATE audit_config SET
            client_id = :client_id,
            agent_users = :agent_users,
            min_call_duration = :min_call_duration,
            max_call_duration = :max_call_duration,
            audit_call_count_per_agent = :audit_call_count_per_agent,
            time_from = :time_from,
            time_to = :time_to,
            call_type = :call_type,
            total_audit_call_count = :total_audit_call_count,
            remaining_audit_call_count = :remaining_audit_call_count,
            dialer_server_ip = :dialer_server_ip,
            updated_at = NOW()
        WHERE id = :id
    """)

    db.execute(query, {
        **data.dict(),
        "remaining_audit_call_count": remaining,
        "id": config_id
    })

    db.commit()

    return {"message": "Audit config updated successfully"}