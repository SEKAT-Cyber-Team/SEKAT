# SEKAT API contract

Backend menggunakan JSON dan timestamp ISO-8601 dengan timezone.

## Autentikasi

- Agent routes: header X-API-Key: <SEKAT_AGENT_API_KEY>.
- Dashboard/admin routes: header X-Admin-Key: <SEKAT_ADMIN_API_KEY>.
- GET /health publik hanya untuk health check dan tidak mengandung informasi rahasia.
- Semua endpoint menggunakan shared agent key pada MVP. Nilai host_id adalah identifier, bukan identitas endpoint yang kuat. Jangan menganggap shared key sebagai autentikasi per perangkat.

## Endpoint

| Method | Path | Auth | Tujuan |
|---|---|---|---|
| GET | /health | none | Health |
| POST | /api/events | agent | Kirim event |
| GET | /api/commands?host=ID | agent | Poll command untuk host |
| POST | /api/commands/ack | agent | Acknowledge command (command_id + host_id harus cocok) |
| GET | /api/hosts | admin | Daftar host |
| GET | /api/events?host=ID&limit=50 | admin | Riwayat event |
| POST | /api/hosts/{host_id}/commands | admin | Queue isolate/release simulasi |
| GET | /api/settings | admin | Baca konfigurasi |

## Event payload

~~~json
{
  "host_id": "lab-endpoint-01",
  "hostname": "lab-vm",
  "ip": "192.0.2.10",
  "timestamp": "2026-11-15T10:00:00+00:00",
  "rule": "R1",
  "severity": "high",
  "risk_score": 40,
  "detail": {
    "distinct_private_peers": ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
  }
}
~~~

Rule yang diterima: HEARTBEAT, R1, R2, R3, R4, STATUS_CHANGE, CMD_ACK. Score 0–100; detail maksimal 4096 byte UTF-8. Timestamp harus menyertakan timezone.

## Command queue

Body untuk queue:
~~~json
{"action":"isolate"}
~~~
atau
~~~json
{"action":"release"}
~~~

Agent melakukan polling untuk host ID yang dikonfigurasi. Acknowledgement:
~~~json
{
  "command_id": 123,
  "host_id": "lab-endpoint-01",
  "status": "applied",
  "detail": "Simulated quarantine; network remains unchanged."
}
~~~

Backend menolak acknowledgement bila host_id berbeda dengan pemilik command. Ini adalah pengaman konsistensi, bukan autentikasi kuat per host, karena semua agent masih memakai shared API key.

Status applied hanya memperbarui status simulasi. Tidak ada aksi OS/jaringan yang dilakukan.
