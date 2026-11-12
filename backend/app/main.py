import hmac, json, os, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Literal
from fastapi import FastAPI, Header, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

AGENT_KEY=os.getenv("SEKAT_AGENT_API_KEY","local-agent-key-change-me")
ADMIN_KEY=os.getenv("SEKAT_ADMIN_API_KEY","local-admin-key-change-me")
DB_PATH=Path(os.getenv("SEKAT_DB_PATH","./data/sekat.db"))
AUTO_ISOLATE=os.getenv("SEKAT_AUTO_ISOLATE","false").lower()=="true"
ORIGINS=[x.strip() for x in os.getenv("SEKAT_CORS_ORIGINS","http://localhost:8080").split(",") if x.strip()]
app=FastAPI(title="SEKAT API",version="1.0.0",description="Defensive lab prototype")
app.add_middleware(CORSMiddleware,allow_origins=ORIGINS,allow_credentials=False,allow_methods=["GET","POST","OPTIONS"],allow_headers=["Content-Type","X-API-Key","X-Admin-Key"])

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def db():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB_PATH,timeout=10); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS hosts(host_id TEXT PRIMARY KEY,hostname TEXT NOT NULL,ip TEXT,last_seen TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'online',risk_score INTEGER NOT NULL DEFAULT 0,quarantine_state TEXT NOT NULL DEFAULT 'none');
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,host_id TEXT NOT NULL,hostname TEXT NOT NULL,ip TEXT,timestamp TEXT NOT NULL,rule TEXT NOT NULL,severity TEXT NOT NULL,risk_score INTEGER NOT NULL,detail TEXT NOT NULL,FOREIGN KEY(host_id) REFERENCES hosts(host_id));
        CREATE INDEX IF NOT EXISTS idx_event_host_time ON events(host_id,timestamp DESC);
        CREATE TABLE IF NOT EXISTS commands(id INTEGER PRIMARY KEY AUTOINCREMENT,host_id TEXT NOT NULL,action TEXT NOT NULL CHECK(action IN ('isolate','release')),status TEXT NOT NULL DEFAULT 'pending',created_at TEXT NOT NULL,acknowledged_at TEXT,FOREIGN KEY(host_id) REFERENCES hosts(host_id));
        CREATE INDEX IF NOT EXISTS idx_cmd_host_status ON commands(host_id,status);
        """)
def agent_auth(x_api_key:str|None=Header(default=None)):
    if not x_api_key or not hmac.compare_digest(x_api_key,AGENT_KEY): raise HTTPException(401,"Invalid agent API key")
def admin_auth(x_admin_key:str|None=Header(default=None)):
    if not x_admin_key or not hmac.compare_digest(x_admin_key,ADMIN_KEY): raise HTTPException(401,"Invalid admin API key")

class EventIn(BaseModel):
    host_id:str=Field(min_length=1,max_length=100)
    hostname:str=Field(min_length=1,max_length=150)
    ip:str|None=Field(default=None,max_length=64)
    timestamp:str=Field(min_length=10,max_length=40)
    rule:Literal["HEARTBEAT","R1","R2","R3","R4","STATUS_CHANGE","CMD_ACK"]
    severity:Literal["info","low","medium","high","critical"]
    risk_score:int=Field(ge=0,le=100)
    detail:dict[str,Any]=Field(default_factory=dict)
class CommandRequest(BaseModel): action:Literal["isolate","release"]
class CommandAck(BaseModel):
    command_id:int
    status:Literal["applied","rejected"]
    detail:str=Field(default="",max_length=500)

@app.on_event("startup")
def startup():
    if os.getenv("SEKAT_ENV","development").lower()=="production":
        placeholders={"local-agent-key-change-me","local-admin-key-change-me","replace-with-a-long-random-agent-key","replace-with-a-long-random-admin-key"}
        if AGENT_KEY in placeholders or ADMIN_KEY in placeholders or min(len(AGENT_KEY),len(ADMIN_KEY))<24:
            raise RuntimeError("Production requires unique API keys of at least 24 characters.")
    init_db()

@app.get("/health")
def health(): return {"status":"ok","service":"sekat-api","time":now()}

@app.post("/api/events",dependencies=[Depends(agent_auth)])
def ingest(e:EventIn):
    try: datetime.fromisoformat(e.timestamp.replace("Z","+00:00"))
    except ValueError: raise HTTPException(422,"timestamp must be ISO-8601")
    with db() as c:
        c.execute("""INSERT INTO hosts(host_id,hostname,ip,last_seen,status,risk_score) VALUES(?,?,?,?, 'online',?)
        ON CONFLICT(host_id) DO UPDATE SET hostname=excluded.hostname,ip=excluded.ip,last_seen=excluded.last_seen,status='online',risk_score=excluded.risk_score""",(e.host_id,e.hostname,e.ip,e.timestamp,e.risk_score))
        c.execute("INSERT INTO events(host_id,hostname,ip,timestamp,rule,severity,risk_score,detail) VALUES(?,?,?,?,?,?,?,?)",(e.host_id,e.hostname,e.ip,e.timestamp,e.rule,e.severity,e.risk_score,json.dumps(e.detail,ensure_ascii=False)))
        if AUTO_ISOLATE and e.risk_score>=70:
            state=c.execute("SELECT quarantine_state FROM hosts WHERE host_id=?",(e.host_id,)).fetchone()["quarantine_state"]
            if state in ("none","released","rejected"):
                c.execute("INSERT INTO commands(host_id,action,status,created_at) VALUES(?,'isolate','pending',?)",(e.host_id,now()))
                c.execute("UPDATE hosts SET quarantine_state='pending' WHERE host_id=?",(e.host_id,))
    return {"accepted":True,"host_id":e.host_id,"rule":e.rule}

@app.get("/api/commands",dependencies=[Depends(agent_auth)])
def commands(host:str=Query(min_length=1,max_length=100)):
    with db() as c:
        rows=c.execute("SELECT id,action,created_at FROM commands WHERE host_id=? AND status='pending' ORDER BY id",(host,)).fetchall()
        if rows: c.executemany("UPDATE commands SET status='delivered' WHERE id=?",[(r["id"],) for r in rows])
    return {"commands":[dict(r) for r in rows]}

@app.post("/api/commands/ack",dependencies=[Depends(agent_auth)])
def ack(a:CommandAck):
    with db() as c:
        r=c.execute("SELECT * FROM commands WHERE id=?",(a.command_id,)).fetchone()
        if not r: raise HTTPException(404,"Command not found")
        if r["status"] not in ("pending","delivered"): raise HTTPException(409,"Command already acknowledged")
        state=("isolated_simulated" if r["action"]=="isolate" else "released") if a.status=="applied" else "rejected"
        c.execute("UPDATE commands SET status=?,acknowledged_at=? WHERE id=?",(a.status,now(),a.command_id))
        c.execute("UPDATE hosts SET quarantine_state=? WHERE host_id=?",(state,r["host_id"]))
    return {"accepted":True,"command_id":a.command_id,"status":a.status}

@app.get("/api/hosts",dependencies=[Depends(admin_auth)])
def hosts():
    with db() as c: rows=c.execute("SELECT * FROM hosts ORDER BY last_seen DESC").fetchall()
    result=[]
    for r in rows:
        item=dict(r)
        try:
            age=(datetime.now(timezone.utc)-datetime.fromisoformat(item["last_seen"].replace("Z","+00:00")).astimezone(timezone.utc)).total_seconds()
            if age>30 and item["quarantine_state"] not in ("pending","isolated_simulated"): item["status"]="offline"
        except (ValueError,TypeError): item["status"]="unknown"
        item["risk_level"]="Kritis" if item["risk_score"]>=70 else "Waspada" if item["risk_score"]>=40 else "Normal"
        result.append(item)
    return {"hosts":result}

@app.get("/api/events",dependencies=[Depends(admin_auth)])
def events(host:str|None=None,limit:int=Query(default=50,ge=1,le=200)):
    with db() as c:
        rows=c.execute("SELECT * FROM events WHERE host_id=? ORDER BY id DESC LIMIT ?",(host,limit)).fetchall() if host else c.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    result=[]
    for r in rows:
        item=dict(r); item["detail"]=json.loads(item["detail"]); result.append(item)
    return {"events":result}

@app.post("/api/hosts/{host_id}/commands",dependencies=[Depends(admin_auth)])
def queue(host_id:str,request:CommandRequest):
    with db() as c:
        host=c.execute("SELECT * FROM hosts WHERE host_id=?",(host_id,)).fetchone()
        if not host: raise HTTPException(404,"Host not found")
        pending=c.execute("SELECT id FROM commands WHERE host_id=? AND status IN ('pending','delivered') ORDER BY id DESC LIMIT 1",(host_id,)).fetchone()
        if pending: raise HTTPException(409,"A command is awaiting acknowledgement")
        if request.action=="release" and host["quarantine_state"] in ("none","released"): raise HTTPException(409,"Host is not quarantined")
        cur=c.execute("INSERT INTO commands(host_id,action,status,created_at) VALUES(?,?,'pending',?)",(host_id,request.action,now()))
        c.execute("UPDATE hosts SET quarantine_state='pending' WHERE host_id=?",(host_id,))
    return {"queued":True,"command_id":cur.lastrowid,"action":request.action}

@app.get("/api/settings",dependencies=[Depends(admin_auth)])
def settings(): return {"auto_isolate":AUTO_ISOLATE,"containment_mode":"simulated","heartbeat_timeout_seconds":30}
