import os,socket
from dataclasses import dataclass
@dataclass(frozen=True)
class Config:
    api_url:str=os.getenv("SEKAT_API_URL","http://127.0.0.1:8000").rstrip("/")
    api_key:str=os.getenv("SEKAT_API_KEY","")
    host_id:str=os.getenv("SEKAT_HOST_ID",socket.gethostname())
    watch_paths:tuple[str,...]=tuple(x.strip() for x in os.getenv("SEKAT_WATCH_PATHS","/tmp/sekat-lab").split(",") if x.strip())
    canary_path:str=os.getenv("SEKAT_CANARY_PATH","/tmp/sekat-lab/SEKAT_CANARY.txt")
    heartbeat:int=max(5,int(os.getenv("SEKAT_HEARTBEAT_SECONDS","10")))
    poll:int=max(2,int(os.getenv("SEKAT_COMMAND_POLL_SECONDS","3")))
    network_sample:int=max(3,int(os.getenv("SEKAT_NETWORK_SAMPLE_SECONDS","5")))
    simulated:bool=os.getenv("SEKAT_SIMULATED_QUARANTINE","true").lower()=="true"
config=Config()
