# API contract
Agent routes require X-API-Key. Dashboard routes require X-Admin-Key. All timestamps use ISO-8601.

| Method | Path | Purpose |
|---|---|---|
| GET | /health | API health |
| POST | /api/events | Agent telemetry |
| GET | /api/commands?host=ID | Agent command polling |
| POST | /api/commands/ack | Agent acknowledgement |
| GET | /api/hosts | Dashboard host list |
| GET | /api/events?host=ID&limit=50 | Dashboard event history |
| POST | /api/hosts/{host_id}/commands | Queue isolate/release |
| GET | /api/settings | Read-only settings |

Example event body:
    {
      "host_id":"lab-endpoint-01",
      "hostname":"lab-vm",
      "ip":"192.0.2.10",
      "timestamp":"2026-11-12T10:00:00+00:00",
      "rule":"R1",
      "severity":"high",
      "risk_score":40,
      "detail":{"distinct_private_peers":["10.0.0.1","10.0.0.2","10.0.0.3"]}
    }

Allowed rules: HEARTBEAT, R1, R2, R3, R4, STATUS_CHANGE, CMD_ACK. Score range is 0-100. Command body: {"action":"isolate"} or {"action":"release"}. A command changes reported host state only after agent acknowledgement. The agent supplied here is simulation-only.
