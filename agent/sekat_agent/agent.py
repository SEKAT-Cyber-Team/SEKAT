import socket,threading,time
from pathlib import Path
import psutil,requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from .config import config
from .detector import Detector

class Handler(FileSystemEventHandler):
    def __init__(self,agent):self.agent=agent
    def on_created(self,e):
        if not e.is_directory:self.agent.file_event(e.src_path,"created")
    def on_modified(self,e):
        if not e.is_directory:self.agent.file_event(e.src_path,"modified")
    def on_deleted(self,e):
        if not e.is_directory:self.agent.file_event(e.src_path,"deleted")
    def on_moved(self,e):
        if not e.is_directory:self.agent.file_event(e.dest_path,"moved")

class Agent:
    def __init__(self,cfg=config):
        if not cfg.api_key:raise ValueError("SEKAT_API_KEY is required")
        self.cfg=cfg;self.detector=Detector(cfg.canary_path);self.hostname=socket.gethostname()
        try:self.ip=socket.gethostbyname(self.hostname)
        except OSError:self.ip="127.0.0.1"
        self.headers={"X-API-Key":cfg.api_key};self.observers=[];self.stopping=threading.Event()
        self.quarantined=False;self.last_sample=0
    def emit(self,item):
        payload={"host_id":self.cfg.host_id,"hostname":self.hostname,"ip":self.ip,**item}
        try:requests.post(self.cfg.api_url+"/api/events",json=payload,headers=self.headers,timeout=5).raise_for_status()
        except requests.RequestException as e:print("[WARN] event delivery:",e)
    def file_event(self,path,kind):
        for item in self.detector.record_file_event(path,kind):self.emit(item)
    def network_sample(self):
        now=time.monotonic()
        if now-self.last_sample<self.cfg.network_sample:return
        self.last_sample=now
        try:peers={c.raddr.ip for c in psutil.net_connections(kind="inet") if c.raddr and c.status==psutil.CONN_ESTABLISHED}
        except (psutil.AccessDenied,OSError) as e:print("[WARN] network observation unavailable:",e);return
        for peer in peers:
            for item in self.detector.record_peer(peer):self.emit(item)
    def poll(self):
        try:
            r=requests.get(self.cfg.api_url+"/api/commands",params={"host":self.cfg.host_id},headers=self.headers,timeout=5);r.raise_for_status()
            for cmd in r.json().get("commands",[]):
                if not self.cfg.simulated:status,detail="rejected","Real containment adapter is not implemented; no system change performed."
                elif cmd["action"]=="isolate":self.quarantined=True;status,detail="applied","Simulated quarantine; network remains unchanged."
                elif cmd["action"]=="release":self.quarantined=False;status,detail="applied","Simulated release; network remains unchanged."
                else:status,detail="rejected","Unsupported command."
                requests.post(self.cfg.api_url+"/api/commands/ack",json={"command_id":cmd["id"],"status":status,"detail":detail},headers=self.headers,timeout=5).raise_for_status()
        except requests.RequestException as e:print("[WARN] command polling:",e)
    def run(self):
        handler=Handler(self)
        for raw in self.cfg.watch_paths:
            root=Path(raw).expanduser().resolve()
            if not root.exists():print("[INFO] watch path skipped:",root);continue
            obs=Observer();obs.schedule(handler,str(root),recursive=True);obs.start();self.observers.append(obs)
        if not self.observers:print("[WARN] no existing watch directory; create it before starting the agent")
        print("[INFO] SEKAT agent started; containment mode is SIMULATED")
        last_heartbeat=0
        try:
            while not self.stopping.is_set():
                now=time.monotonic();self.network_sample();self.poll()
                if self.detector.decay():self.emit(self.detector.event("STATUS_CHANGE",{"reason":"risk_decay"}))
                if now-last_heartbeat>=self.cfg.heartbeat:
                    self.emit(self.detector.event("HEARTBEAT",{"quarantined_simulated":self.quarantined}));last_heartbeat=now
                self.stopping.wait(1)
        except KeyboardInterrupt:pass
        finally:
            self.stopping.set()
            for o in self.observers:o.stop()
            for o in self.observers:o.join(timeout=3)
def main():Agent().run()
if __name__=="__main__":main()
