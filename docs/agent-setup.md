# Agent setup (disposable lab VM)
Do not test containment on production or your everyday laptop. The agent is an observer and simulated-command client.

1. Clone the repository inside a disposable VM.
2. Install Python 3.11+, then run:
       cd SEKAT/agent
       python -m venv .venv
       source .venv/bin/activate
       pip install -r requirements.txt
3. Copy agent/.env.example to agent/.env. Set SEKAT_API_URL to a host address reachable from the VM and SEKAT_API_KEY to the root SEKAT_AGENT_API_KEY.
4. Create the scoped test folder and marker:
       mkdir -p /tmp/sekat-lab
       printf 'SEKAT demo canary - harmless marker\n' > /tmp/sekat-lab/SEKAT_CANARY.txt
5. Load environment variables and start:
       set -a; source .env; set +a
       python -m sekat_agent

Keep SEKAT_WATCH_PATHS limited to the lab folder and SEKAT_SIMULATED_QUARANTINE=true. With false, the agent rejects commands. No real isolation adapter exists.

Network note: Compose binds API and dashboard to localhost by default. For an agent in another VM, deliberately bind port 8000 to the host-only lab interface IP and restrict the firewall to that isolated network. Never bind the API to a public interface.
