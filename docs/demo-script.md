# Demo script (4-5 minutes)
Opening: "SEKAT is an early-warning and containment coordination prototype. It observes a deliberately scoped lab endpoint, assigns risk and coordinates a response. This demonstration uses synthetic telemetry and simulated quarantine."

1. Problem (30s): ransomware can spread over shared services; visibility and response coordination matter.
2. Architecture (45s): endpoint agent -> API/SQLite -> dashboard; simulator sends safe test events.
3. Normal state (30s): send normal event and show endpoint heartbeat.
4. Detection (90s): submit R1, R2 and R3 scenarios; explain thresholds, score increments and Waspada/Kritis.
5. Containment (60s): click Isolate, show queued command and acknowledgement. Clearly state no interface or firewall is changed. Click Release.
6. Engineering (45s): show API keys, tests, Compose and limitations.
7. Close (20s): "SEKAT demonstrates a safety-first detection-to-response workflow in an isolated lab."

Recording: 1920x1080, 100% zoom, load synthetic hosts first, hide secrets, verify labels and scores. Never claim real quarantine or malware prevention. Disclaimer: Synthetic telemetry | Simulated containment | Isolated lab demo.
