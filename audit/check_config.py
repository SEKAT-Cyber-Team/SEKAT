from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
env=(root/".env.example").read_text()
agent_env=(root/"agent"/".env.example").read_text()
backend=(root/"backend"/"app"/"main.py").read_text()
agent=(root/"agent"/"sekat_agent"/"agent.py").read_text()
gitignore=(root/".gitignore").read_text()

checks={
 "Auto-isolation disabled by default":"SEKAT_AUTO_ISOLATE=false" in env,
 "Backend API binds to loopback by default":"SEKAT_BIND_HOST=127.0.0.1" in env,
 "Agent simulated containment enabled by default":"SEKAT_SIMULATED_QUARANTINE=true" in agent_env,
 "Agent reports host ID in command acknowledgement":'"host_id":self.cfg.host_id' in agent,
 "Backend verifies command ownership against host ID":'r["host_id"]!=a.host_id' in backend,
 "Backend limits event detail payload":'4096 UTF-8 bytes' in backend,
 "Real containment adapter intentionally absent":"Real containment adapter is not implemented" in agent,
 "Local secrets ignored by Git":".env" in gitignore and "agent/.env" in gitignore,
}
failed=False
for name,ok in checks.items():
 print("[PASS]" if ok else "[FAIL]",name)
 failed |= not ok
print("Advisory configuration hygiene check only; not a full security audit.")
sys.exit(1 if failed else 0)
