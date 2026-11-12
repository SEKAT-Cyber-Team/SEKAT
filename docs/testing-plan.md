# Test and acceptance plan

## Automated checks

- Backend: install `backend/requirements.txt`, then run `PYTHONPATH=. pytest -q` from `backend/`.
- Agent: install `agent/requirements.txt`, then run `PYTHONPATH=. pytest -q` from `agent/`.
- Configuration: run `python audit/check_config.py` from the repository root.
- Dashboard: run `npm install && npm run build` from `dashboard/`.
- Containers: run `cp .env.example .env`, `docker compose config --quiet` and `docker compose build`.

GitHub Actions runs these checks on pushes and pull requests. A green CI run proves the automated checks and image builds completed in GitHub's runner; it does not prove runtime behavior on the team's Parrot OS or VM network.

## Manual lab acceptance

1. Start Compose; confirm the backend `/health` endpoint and dashboard load.
2. Submit simulator scenarios `normal`, `scan`, `file-burst`, `canary`, `critical` and `audit` with different host IDs.
3. Confirm hosts, events, risk scores and severity appear in the dashboard.
4. Run an agent against a disposable VM's scoped `/tmp/sekat-lab` directory. Modify the canary marker and create harmless test files to trigger R2/R3.
5. Confirm heartbeats and events arrive at the controller.
6. Queue Isolate and Release for an agent-backed endpoint; confirm acknowledgements and simulated state changes.
7. Verify endpoint networking, firewall rules and interfaces remain unchanged.
8. For a separate endpoint VM, verify API connectivity only over the host-only network and confirm port 8000 is not reachable from public networks.

## Negative checks

- Missing/wrong agent key -> 401.
- Missing/wrong admin key -> 401.
- Invalid event rule or out-of-range score -> validation error.
- Duplicate pending command -> 409.
- `.env`, database files, virtual environments and `node_modules` must not be committed.

## Acceptance boundary

The MVP is ready for team runtime validation when health works, telemetry persists, detector/API tests pass, the command queue round-trip works, dashboard builds, and no destructive malware or real quarantine is used. It is not a production endpoint security product and has not been validated on the team's physical/virtual lab until the manual tests above are run.
