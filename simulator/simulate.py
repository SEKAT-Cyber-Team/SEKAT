#!/usr/bin/env python3
"""Send harmless synthetic SEKAT telemetry. No malware, scanning, or file changes."""
import argparse,os,socket
from datetime import datetime,timezone
import requests

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--api",default=os.getenv("SEKAT_API_URL","http://127.0.0.1:8000"))
 p.add_argument("--key",default=os.getenv("SEKAT_API_KEY",""))
 p.add_argument("--host-id",default="simulated-endpoint-01")
 p.add_argument("--scenario",choices=["normal","scan","file-burst","canary","critical","audit"],default="normal")
 a=p.parse_args()
 if not a.key:p.error("provide --key or SEKAT_API_KEY")
 samples={
 "normal":("HEARTBEAT",0,"info",{"scenario":"synthetic heartbeat"}),
 "scan":("R1",40,"high",{"distinct_private_peers":["10.10.0.11","10.10.0.12","10.10.0.13"],"synthetic":True}),
 "file-burst":("R2",35,"medium",{"file_events":34,"window_seconds":10,"synthetic":True}),
 "canary":("R3",60,"high",{"canary":"DEMO_CANARY","synthetic":True}),
 "critical":("R3",75,"critical",{"canary":"DEMO_CANARY","synthetic":True}),
 "audit":("R4",15,"low",{"finding":"Synthetic operator audit finding","synthetic":True})}
 rule,score,severity,detail=samples[a.scenario]
 payload={"host_id":a.host_id,"hostname":socket.gethostname(),"ip":"192.0.2.25","timestamp":datetime.now(timezone.utc).isoformat(),"rule":rule,"severity":severity,"risk_score":score,"detail":detail}
 response=requests.post(a.api.rstrip("/")+"/api/events",json=payload,headers={"X-API-Key":a.key},timeout=8)
 response.raise_for_status()
 print("Accepted",rule,"risk",score,"severity",severity)
if __name__=="__main__":main()
