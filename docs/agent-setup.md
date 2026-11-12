# Agent setup (disposable lab VM)

The agent runs on the endpoint being monitored. The backend and dashboard run in Docker Compose on the controller/host machine. Do not test containment on production or your everyday laptop: this build only simulates quarantine and never changes endpoint networking.

## 1. Configure the controller

1. Copy the repository root `.env.example` to `.env`.
2. Generate two different random API keys (at least 24 characters), then set `SEKAT_AGENT_API_KEY` and `SEKAT_ADMIN_API_KEY`. Never commit `.env`.
3. For an agent running on the **same machine**, keep `SEKAT_BIND_HOST=127.0.0.1`.
4. For an agent in a **separate disposable VM**, find the controller machine's IP address on its host-only lab interface (for example with `ip -4 addr`). Set `SEKAT_BIND_HOST` in the controller's `.env` to that specific IP address. Do not use `0.0.0.0`.
5. Start or recreate the services after changing the bind address:
   ```bash
   docker compose up --build -d
   docker compose ps
   curl http://127.0.0.1:8000/health
   ```
6. Restrict the controller firewall so port 8000 accepts connections only from the isolated host-only lab subnet. Do not expose the API on a public interface. The dashboard remains bound to controller localhost at `http://localhost:8080`.

## 2. Prepare the endpoint VM

1. Clone the repository inside a disposable VM and install Python 3.11+.
2. Create and activate a virtual environment:
   ```bash
   cd SEKAT/agent
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
3. Edit `agent/.env`:
   - `SEKAT_API_URL=http://127.0.0.1:8000` when controller and agent are on the same machine.
   - For a separate VM, use `http://<CONTROLLER_HOST_ONLY_IP>:8000`.
   - Set `SEKAT_API_KEY` to the exact value of the controller's `SEKAT_AGENT_API_KEY`.
   - Keep `SEKAT_SIMULATED_QUARANTINE=true`.
   - Keep `SEKAT_WATCH_PATHS` limited to the test folder.
4. Create a harmless marker:
   ```bash
   mkdir -p /tmp/sekat-lab
   printf 'SEKAT demo canary - harmless marker\n' > /tmp/sekat-lab/SEKAT_CANARY.txt
   ```
5. Load the agent configuration and start it:
   ```bash
   set -a
   source .env
   set +a
   python -m sekat_agent
   ```

The agent observes only configured directories and established connections visible to its process. If the OS denies access to connection information, it logs a warning and skips that sample; do not broaden privileges or watch paths on your daily-use machine.

## 3. Confirm connectivity

- Controller local health check: `curl http://127.0.0.1:8000/health`.
- Dashboard: open `http://localhost:8080` and enter `SEKAT_ADMIN_API_KEY`.
- From a separate VM, verify `curl http://<CONTROLLER_HOST_ONLY_IP>:8000/health` before starting the agent.
- The dashboard key is held in browser session storage and is cleared when the console is locked or the browser session ends.

## Safety boundary

`SEKAT_SIMULATED_QUARANTINE=true` means an isolate/release command changes only an in-memory simulation flag and sends an acknowledgement. It does not block packets, change firewall rules, disable interfaces, kill processes or stop services. No real isolation adapter is included in this MVP.
