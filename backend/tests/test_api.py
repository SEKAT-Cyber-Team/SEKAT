from datetime import datetime,timezone
from fastapi.testclient import TestClient
import app.main as main

def test_event_command_flow(tmp_path,monkeypatch):
    monkeypatch.setattr(main,"DB_PATH",tmp_path/"test.db")
    main.init_db()
    client=TestClient(main.app)
    agent={"X-API-Key":main.AGENT_KEY}; admin={"X-Admin-Key":main.ADMIN_KEY}
    payload={"host_id":"test-host","hostname":"lab-vm","ip":"192.0.2.10","timestamp":datetime.now(timezone.utc).isoformat(),"rule":"R3","severity":"critical","risk_score":75,"detail":{"source":"test"}}
    assert client.get("/health").status_code==200
    assert client.post("/api/events",json=payload).status_code==401
    assert client.post("/api/events",json=payload,headers=agent).status_code==200
    assert client.get("/api/hosts",headers=admin).json()["hosts"][0]["risk_level"]=="Kritis"
    command=client.post("/api/hosts/test-host/commands",json={"action":"isolate"},headers=admin)
    assert command.status_code==200
    cid=command.json()["command_id"]
    assert client.get("/api/commands?host=test-host",headers=agent).json()["commands"][0]["id"]==cid
    assert client.post("/api/commands/ack",json={"command_id":cid,"status":"applied"},headers=agent).status_code==200
    assert client.get("/api/hosts",headers=admin).json()["hosts"][0]["quarantine_state"]=="isolated_simulated"
