#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

for cmd in docker curl openssl python3; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "[ERROR] Required command not found: $cmd" >&2; exit 1; }
done
docker compose version >/dev/null 2>&1 || { echo "[ERROR] Docker Compose plugin is unavailable." >&2; exit 1; }

if [[ ! -f .env ]]; then
  cp .env.example .env
  AGENT_KEY="$(openssl rand -hex 32)"
  ADMIN_KEY="$(openssl rand -hex 32)"
  python3 - "$AGENT_KEY" "$ADMIN_KEY" <<'PY'
from pathlib import Path
import sys
path = Path('.env')
agent, admin = sys.argv[1:3]
lines = path.read_text().splitlines()
updates = {'SEKAT_AGENT_API_KEY': agent, 'SEKAT_ADMIN_API_KEY': admin, 'SEKAT_BIND_HOST': '127.0.0.1'}
seen = set()
out = []
for line in lines:
    if '=' in line and not line.lstrip().startswith('#'):
        key = line.split('=', 1)[0]
        if key in updates:
            out.append(f'{key}={updates[key]}')
            seen.add(key)
            continue
    out.append(line)
for key, value in updates.items():
    if key not in seen:
        out.append(f'{key}={value}')
path.write_text('\n'.join(out) + '\n')
PY
  chmod 600 .env
  echo "[OK] Created local .env with fresh API keys."
else
  echo "[INFO] Existing .env found; keeping its credentials."
fi

set -a
source .env
set +a
: "${SEKAT_AGENT_API_KEY:?SEKAT_AGENT_API_KEY is missing in .env}"
: "${SEKAT_ADMIN_API_KEY:?SEKAT_ADMIN_API_KEY is missing in .env}"

echo "[1/3] Building and starting SEKAT backend + dashboard..."
docker compose up --build -d

echo "[2/3] Waiting for API health..."
HEALTHY=0
for _ in $(seq 1 40); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null; then HEALTHY=1; break; fi
  sleep 2
done
if [[ "$HEALTHY" -ne 1 ]]; then
  echo "[ERROR] API did not become healthy. Inspect with: docker compose logs --tail=100" >&2
  exit 1
fi

echo "[3/3] Sending synthetic demonstration events..."
python3 - <<'PY'
import json, os, urllib.request, datetime
base = 'http://127.0.0.1:8000'
key = os.environ['SEKAT_AGENT_API_KEY']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
events = [
  ('demo-normal', 'HEARTBEAT', 'info', 10, {'scenario':'synthetic normal heartbeat'}),
  ('demo-peer-spread', 'R1', 'high', 40, {'scenario':'synthetic peer-spread example','distinct_private_peers':['10.10.0.11','10.10.0.12','10.10.0.13'],'window_seconds':20}),
  ('demo-file-burst', 'R2', 'medium', 35, {'scenario':'synthetic file-burst example','file_events':34,'window_seconds':10}),
  ('demo-canary', 'R3', 'high', 60, {'scenario':'synthetic canary example','canary':'DEMO_CANARY'}),
  ('demo-critical', 'R3', 'critical', 75, {'scenario':'synthetic critical-risk example','canary':'DEMO_CANARY'}),
  ('demo-audit', 'R4', 'low', 15, {'scenario':'synthetic operator audit finding'}),
]
for host, rule, severity, score, detail in events:
    payload = {'host_id':host,'hostname':host,'ip':'192.0.2.25','timestamp':now,'rule':rule,'severity':severity,'risk_score':score,'detail':detail}
    req = urllib.request.Request(base+'/api/events', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json','X-API-Key':key}, method='POST')
    with urllib.request.urlopen(req, timeout=8) as response:
        if response.status != 200: raise RuntimeError(f'{host}: HTTP {response.status}')
    print(f'[OK] {host}: {rule}, risk {score}')
PY

echo
echo "SEKAT demo is ready: http://localhost:8080"
echo "Enter the SEKAT_ADMIN_API_KEY value from .env in the dashboard."
echo "All displayed endpoints/events are synthetic. This script does not start an endpoint agent or perform real isolation."
echo "To stop services later: docker compose down"
