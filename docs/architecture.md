# Architecture
- Endpoint agent: runs on a disposable lab VM, watches only configured directories, observes established IPv4 connections, applies deterministic R1-R3 rules and polls commands.
- Backend: FastAPI, X-API-Key for agents, X-Admin-Key for dashboard, SQLite event/host/command persistence.
- Dashboard: React/Vite + Nginx; fleet state, event stream, risk levels and command controls.
- Simulator: harmless synthetic event generator.
- Docker Compose: backend and dashboard only. Agent runs separately on its endpoint.

Flow: Agent -> POST /api/events -> API/SQLite -> dashboard GET /api/hosts and GET /api/events. Dashboard -> POST /api/hosts/{host_id}/commands -> queue -> agent GET /api/commands?host=ID -> simulated command -> POST /api/commands/ack.

Risk: R1 +40, R2 +35, R3 +60, R4 +15; capped at 100. Normal 0-39, Waspada 40-69, Kritis 70-100. R1-R3 decay by 10 every 30 seconds; R4 persists. Agent risk state is in memory and resets on restart. Backend stores the latest score and event history.

Safety: containment is a simulated in-memory flag; no firewall or interface changes. No malware, exploit, mass-encryption or process-kill code. File monitoring is scoped to SEKAT_WATCH_PATHS. R4 is operator-submitted, not automatic privileged audit. SQLite is single-node demo storage. API keys are not production IAM/TLS.
