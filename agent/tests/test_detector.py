from sekat_agent.detector import Detector
class Clock:
 def __init__(self):self.t=0
 def __call__(self):return self.t
 def tick(self,n):self.t+=n
def test_r1_and_decay(tmp_path):
 c=Clock();d=Detector(str(tmp_path/"CANARY"),c)
 assert d.record_peer("10.0.0.1")==[] and d.record_peer("10.0.0.2")==[]
 assert d.record_peer("10.0.0.3")[0]["rule"]=="R1" and d.risk_score==40
 c.tick(30);assert d.decay() and d.risk_score==30
def test_r2_r3(tmp_path):
 c=Clock();canary=tmp_path/"CANARY";d=Detector(str(canary),c)
 for i in range(29):assert d.record_file_event(str(tmp_path/f"f{i}"),"changed")==[]
 assert d.record_file_event(str(tmp_path/"last"),"changed")[0]["rule"]=="R2"
 assert d.record_file_event(str(canary),"modified")[0]["rule"]=="R3"
