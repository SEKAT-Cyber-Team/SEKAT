# Architecture

## Components

- **Endpoint Agent (Python):** runs on a disposable lab VM; watches only configured directories, observes established connections visible to the process, evaluates R1-R3, emits heartbeat and polls commands.
- **Backend (FastAPI):** accepts agent telemetry, applies API-key checks, persists hosts/events/commands in SQLite, exposes dashboard read APIs and queues operator commands.
- **Dashboard (React/Vite + Nginx):** displays endpoint status, risk, event history, and simulated response controls.
- **Simulator:** submits harmless synthetic event payloads. It does not replace endpoint-agent testing.
- **Docker Compose:** runs backend and dashboard. The endpoint agent is installed and run separately on the endpoint.

## Data flow

~~~text
Endpoint Agent -> POST /api/events -> FastAPI -> SQLite
      ^                                |
      | GET /api/commands?host=ID       | GET /api/hosts and /api/events
      |                                v
      +-- POST /api/commands/ack <- Dashboard / Operator
                 |
                 +-- command acknowledgement and simulated state
~~~

A command remains eligible for delivery while its status is pending or delivered. This means an agent that restarts before acknowledgement can receive it again. Isolate/release simulation is idempotent; backend stops redelivery after an acknowledgement.

## Detection and scoring

- R1: 3 or more distinct private IPv4 peers observed in 20 seconds (+40).
- R2: 30 or more filesystem events in 10 seconds under watched directories (+35).
- R3: configured canary path touched (+60; once per agent process).
- R4: audit-finding event (+15; submitted/simulated event, not a privileged automatic audit integration).

Risk is clamped to 0-100. Normal 0-39, Waspada 40-69, Kritis 70-100. R1-R3 decay by 10 points every 30 seconds; R4 persists. Agent detector state is in memory and resets on restart. Backend stores received event history and the most recent received host score.

## Identity and authorization boundary

- Agent routes use one shared SEKAT_AGENT_API_KEY across all endpoints.
- Dashboard routes use one SEKAT_ADMIN_API_KEY.
- Command acknowledgement now requires both command_id and host_id to match the queued command's owner. This protects against accidental/mismatched acknowledgements.
- **This does not provide strong per-device identity:** any holder of the shared agent key can still claim another host_id or poll that host's queue. Keep the system on localhost or a trusted isolated Host-Only lab network.
- No TLS, rate limiting, RBAC, enrollment, per-agent credential rotation, or production IAM is included.

## Safety boundary

Containment is a simulated in-memory flag only. No firewall, routing table, interface, process, or OS service is changed. There is no malware, exploit, mass-encryption or process-kill logic. File monitoring is scoped to SEKAT_WATCH_PATHS. Connection visibility depends on OS permissions and psutil visibility.

## Storage and scale

SQLite is a simple single-node demo store, not an HA or high-throughput database. Commands/events have no production-grade retention/quotas. This architecture is an MVP for isolated lab evaluation, not an internet-facing service or production endpoint security platform.
