# Safe synthetic simulator
Install with python -m pip install -r requirements.txt. Set SEKAT_API_KEY to the same value as SEKAT_AGENT_API_KEY from the root .env.

Examples:
    python simulate.py --scenario normal
    python simulate.py --scenario scan --host-id demo-scan
    python simulate.py --scenario file-burst --host-id demo-files
    python simulate.py --scenario canary --host-id demo-canary
    python simulate.py --scenario critical --host-id demo-critical
    python simulate.py --scenario audit --host-id demo-audit

It submits one synthetic telemetry payload. It does not scan networks, create file changes, access a real canary, or run malware.
