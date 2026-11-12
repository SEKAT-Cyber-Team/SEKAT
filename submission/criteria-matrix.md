# Evaluation Criteria Matrix — SEKAT

The weights below are from the Kartika Cyber Hackathon 2026 rulebook. This matrix distinguishes implemented behavior from evidence that still requires a live lab run.

| Criterion | Weight | SEKAT response | Evidence to show | Honest limitation |
|---|---:|---|---|---|
| Relevance & benefits | 25% | Early warning for unusual endpoint connection patterns and rapid file activity; centralized risk visibility and response coordination. | Problem statement, architecture, dashboard event/risk view, R1-R4 flow. | This is a lab prototype, not a deployed TNI AD operational system. |
| Technical innovation | 25% | Explainable R1-R4 rules, risk scoring, agent telemetry, persistent event history and command acknowledgement. | Detector source, API, simulator scenarios, risk table. | Rules are deterministic and scoped; no claim of AI-powered autonomous detection. |
| Prototype functionality | 25% | Working code paths for agent, API, dashboard, simulator and simulated command queue; automated checks pass in CI. | GitHub Actions checks and simulator walkthrough. | Manual Parrot OS + VM end-to-end run has not yet been completed. |
| Implementation feasibility | 15% | Endpoint agent separated from controller; FastAPI + SQLite; Docker Compose for backend/dashboard; configurable host-only lab connection. | Architecture and setup documentation. | Operational deployment needs TLS, access hardening, monitoring and validation in the target environment. |
| Documentation quality | 10% | README, API guide, architecture, testing plan, demo script, presentation and video materials. | Repository docs, slide deck, thumbnail and YouTube video. | UI previews in the generated pack are illustrative and marked synthetic; use genuine interface screenshots if available. |

## Current MVP behavior
- R1: 3 or more distinct private IPv4 peers within 20 seconds; +40 points.
- R2: 30 or more file events within 10 seconds; +35 points.
- R3: configured canary file touched; +60 points.
- R4: operator-supplied audit finding; +15 points.
- Risk levels: Normal 0-39, Waspada 40-69, Kritis 70-100.
- R1-R3 decay by 10 points every 30 seconds; R4 persists.
- Auto-isolate is disabled by default. When enabled, it queues a simulated isolate command only.
- Isolate/release acknowledgements update simulated state. No firewall, network interface or host route is modified.

## Safe demo scenarios
Use simulator scenarios with distinct host IDs. Do not present synthetic events as telemetry collected from real malware or real lateral movement. The endpoint agent must only watch a dedicated disposable lab directory.