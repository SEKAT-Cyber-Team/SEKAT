# Security notes and threat model

SEKAT adalah prototipe defensif untuk laboratorium terisolasi. Jangan gunakan untuk melindungi jaringan produksi atau endpoint yang berisi data penting.

## Safety properties in this MVP

- No malware execution, file encryption/deletion, process termination, active network scanning, firewall/routing changes, or interface disabling.
- Folder monitoring is scoped by SEKAT_WATCH_PATHS.
- SEKAT_AUTO_ISOLATE=false by default.
- Agent quarantine simulation is enabled by default; isolate/release affects only an in-memory flag.
- API binds to 127.0.0.1 by default. A separate lab VM requires a specific Host-Only controller IP and host firewall rule.
- .env and runtime data are ignored by Git.

## Known limitations / residual risks

| Area | Current limitation | Consequence |
|---|---|---|
| Agent identity | One shared agent API key across all hosts | Any holder can impersonate another host ID or poll its queued commands |
| Transport | HTTP; no TLS | Traffic is not encrypted; keep it on localhost/isolated Host-Only network |
| Authorization | One admin key, no user/role model | No operator separation or fine-grained permissions |
| Abuse controls | No rate limiting or quotas | An authorized/misused client can submit excessive events |
| Detector | Heuristic thresholds and in-memory state | False positives/negatives; state resets on restart |
| Endpoint visibility | OS permission-dependent connection observation | Some connections may not be visible |
| Storage | SQLite single-node demo database | Not designed for HA or high-volume multi-host production |
| Containment | Simulated only | No actual network protection or isolation |

## Required deployment precautions

1. Keep the system in an isolated lab.
2. Generate separate random agent/admin keys, each at least 24 characters.
3. Never commit .env, logs containing sensitive details, database files or endpoint data.
4. Keep SEKAT_AUTO_ISOLATE=false during testing.
5. Do not expose port 8000 or the dashboard directly to the internet.
6. Use only harmless marker files and synthetic telemetry.
7. Review all limitations before making any claim about protection or containment.

## Production readiness

This codebase is **not production-ready**. A future production design would require per-device identity/enrollment, TLS, RBAC, rate limits, key rotation/revocation, hardened storage, security logging, threat modeling, code review, platform-specific agent validation, and a real containment adapter with explicit authorization and rollback safeguards. No such functionality is claimed by this project.
