from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
checks={
 "Auto-isolation disabled by default":"SEKAT_AUTO_ISOLATE=false" in (root/".env.example").read_text(),
 "Agent containment simulation enabled by default":"SEKAT_SIMULATED_QUARANTINE=true" in (root/".env.example").read_text(),
 "Real containment adapter intentionally absent":"Real containment adapter is not implemented" in (root/"agent/sekat_agent/agent.py").read_text()
}
failed=False
for name,ok in checks.items():
 print("[PASS]" if ok else "[FAIL]",name);failed|=not ok
print("Advisory only; not a complete security audit.")
sys.exit(1 if failed else 0)
