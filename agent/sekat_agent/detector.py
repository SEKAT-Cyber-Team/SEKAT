from collections import deque
from datetime import datetime,timezone
from pathlib import Path
import ipaddress,time

class Detector:
    def __init__(self,canary_path,clock=time.monotonic):
        self.canary=str(Path(canary_path).resolve()); self.clock=clock
        self.files=deque(); self.peers=deque(); self.parts={"R1":0,"R2":0,"R3":0,"R4":0}; self.last_decay=clock(); self.canary_seen=False
    @property
    def risk_score(self): return min(100,max(0,sum(self.parts.values())))
    def event(self,rule,detail):
        score=self.risk_score
        return {"rule":rule,"severity":"critical" if score>=70 else "high" if score>=40 else "info","risk_score":score,"timestamp":datetime.now(timezone.utc).isoformat(),"detail":detail}
    def add(self,rule,points,detail):
        self.parts[rule]=min(100,self.parts[rule]+points)
        return self.event(rule,{"points_added":points,**detail})
    def record_peer(self,address):
        try: ip=ipaddress.ip_address(address)
        except ValueError: return []
        if ip.version!=4 or not ip.is_private or ip.is_loopback or ip.is_link_local: return []
        now=self.clock(); self.peers.append((now,str(ip)))
        while self.peers and now-self.peers[0][0]>20: self.peers.popleft()
        unique={x for _,x in self.peers}
        return [self.add("R1",40,{"distinct_private_peers":sorted(unique),"window_seconds":20})] if len(unique)>=3 and self.parts["R1"]==0 else []
    def record_file_event(self,path,kind):
        now=self.clock()
        if str(Path(path).resolve())==self.canary and not self.canary_seen:
            self.canary_seen=True; return [self.add("R3",60,{"path":self.canary,"event_type":kind})]
        self.files.append(now)
        while self.files and now-self.files[0]>10: self.files.popleft()
        return [self.add("R2",35,{"file_events":len(self.files),"window_seconds":10})] if len(self.files)>=30 and self.parts["R2"]==0 else []
    def audit(self,finding): return self.add("R4",15,{"finding":finding[:300]})
    def decay(self):
        now=self.clock(); n=int((now-self.last_decay)//30)
        if n<=0:return False
        for key in ("R1","R2","R3"):self.parts[key]=max(0,self.parts[key]-10*n)
        self.last_decay+=30*n
        return True
