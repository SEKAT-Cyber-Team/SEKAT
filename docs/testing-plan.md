# Test and acceptance plan
Automated: install backend requirements and run PYTHONPATH=. pytest -q from backend; install agent requirements and run PYTHONPATH=. pytest -q from agent; run python audit/check_config.py; build dashboard with npm install and npm run build.

Manual:
1. Start Compose; confirm /health.
2. Submit simulator scenarios normal, scan, file-burst, canary, critical and audit using different host IDs.
3. Confirm hosts, events, risk and severity appear in dashboard.
4. With an agent running for a simulated host, queue Isolate and confirm isolated_simulated after acknowledgement.
5. Queue Release and confirm released.
6. Verify endpoint networking is unchanged.

Negative checks: missing/wrong agent key -> 401; missing/wrong admin key -> 401; invalid rule/score -> validation error; duplicate pending command -> 409; .env/database/virtualenv/node_modules must not be committed.

Acceptance: health works, telemetry persists, rule tests pass, command queue round-trip works, dashboard builds, and no destructive malware or real quarantine is used.
