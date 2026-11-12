# SEKAT — Sistem Early-warning & Karantina Anti-Tular Ransomware

Defensive prototype for a disposable lab: endpoint telemetry, deterministic risk scoring, an event dashboard and simulated containment commands.

**Safety:** this build uses synthetic telemetry and simulated quarantine only. It does not encrypt files, execute malware, scan networks, kill processes, change firewall rules or disable interfaces. Use isolated lab endpoints and narrowly scoped watch folders.

## Included
- Python endpoint agent with heartbeat, scoped file monitoring, connection observation, R1-R4 rules, command polling and simulated acknowledgement.
- FastAPI service with agent/admin key authentication and SQLite persistence.
- React dashboard with endpoint health, risk levels, event history and isolate/release controls.
- Synthetic simulator, tests, Docker Compose and demo documentation.

## Start backend + dashboard
1. Copy .env.example to .env and set unique random values for both API keys.
2. Run: docker compose up --build -d
3. Open http://localhost:8080 and enter SEKAT_ADMIN_API_KEY.
4. Follow docs/agent-setup.md to run the agent inside a disposable lab VM.
5. Generate safe test events using simulator/simulate.py.

Do not expose the API/dashboard directly to the public internet. Production use requires TLS, stronger access control, rate limits, key rotation and a security review.

## Rules
R1: 3+ distinct private IPv4 peers / 20s (+40); R2: 30+ file events / 10s (+35); R3: configured canary touched (+60); R4: operator-supplied audit finding (+15). Scores clamp to 0-100. Normal 0-39, Waspada 40-69, Kritis 70-100. R1-R3 decay by 10 every 30s; R4 persists. Auto-isolate is off by default and queues simulated commands only.

See docs/architecture.md, docs/testing-plan.md and docs/demo-script.md. Submission preparation: see submission/README.md, submission/criteria-matrix.md and submission/video-script-id.md.
