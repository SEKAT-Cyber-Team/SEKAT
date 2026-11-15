# SEKAT
## Sistem Early-warning & Karantina Anti-Tular Ransomware

**SEKAT** adalah prototipe keamanan siber defensif untuk laboratorium terisolasi. Sistem mengumpulkan telemetri endpoint, mendeteksi beberapa indikator perilaku mencurigakan, menghitung skor risiko, menampilkan peristiwa pada dashboard, dan mengantrekan perintah respons yang **disimulasikan**.

> **Batas keselamatan:** fitur isolate/release pada versi ini TIDAK melakukan karantina jaringan sungguhan. Agent hanya mengubah flag simulasi di memori dan mengirim acknowledgement. SEKAT tidak mengubah firewall/routing, mematikan interface, menghentikan proses, mengenkripsi/menghapus file, menjalankan malware, atau melakukan pemindaian jaringan aktif.

- **Status:** defensive lab prototype / MVP
- **Runtime utama:** Docker Compose (backend + dashboard) dan Python endpoint agent
- **Penyimpanan:** SQLite
- **Lisensi:** MIT — lihat LICENSE

---

## 1. Fitur

| Komponen | Fungsi |
|---|---|
| Endpoint Agent (Python) | Heartbeat, pemantauan folder terpilih, observasi koneksi established yang terlihat oleh proses agent, deteksi R1–R3, polling perintah dan acknowledgement simulasi |
| Detection Engine | Rule deterministik R1–R4, risk score 0–100, decay skor |
| Backend API (FastAPI) | Autentikasi API key agent/admin, menerima event, menyimpan endpoint/event/perintah ke SQLite |
| Dashboard (React + Vite + Nginx) | Status endpoint, level risiko, event stream, antrean Isolate/Release simulasi |
| Synthetic Simulator | Mengirim data uji Normal, Scan, File Burst, Canary, Critical, dan Audit tanpa menjalankan malware |
| Docker Compose | Menjalankan backend dan dashboard dalam jaringan Docker internal |
| GitHub Actions | Tes unit agent/backend, build dashboard, pemeriksaan konfigurasi, validasi dan build container |

## 2. Arsitektur

~~~text
 [Endpoint VM / Host Lab]
       Python Agent
       | - scoped folder watcher
       | - established connection observation
       | - R1/R2/R3 + heartbeat
       v
 [FastAPI Backend] <---- [Synthetic Simulator]
       |  Agent/Admin API Key
       |  Event + Host + Command API
       v
    [SQLite]
       ^
       | dashboard API
 [React Dashboard]
       |
       +-- operator queues simulated isolate/release
       +-- agent polls command and acknowledges
~~~

Docker Compose hanya menjalankan **backend dan dashboard**. Agent dijalankan terpisah pada endpoint lab yang dipantau. Simulator hanya mengirim event sintetis; simulator bukan pengganti pengujian agent.

## 3. Rule deteksi dan risk score

| Rule | Indikator | Tambahan skor |
|---|---|---:|
| R1 | Minimal 3 alamat IPv4 private berbeda yang teramati dalam 20 detik | +40 |
| R2 | Minimal 30 event file dalam 10 detik pada folder pantauan | +35 |
| R3 | Canary file yang dikonfigurasi disentuh | +60 |
| R4 | Temuan audit yang dikirim/disimulasikan sebagai event R4 (bukan audit otomatis agent) | +15 |

Skor dijumlahkan dan dibatasi pada 0–100. Level: **Normal 0–39**, **Waspada 40–69**, **Kritis 70–100**. Skor R1–R3 berkurang 10 poin setiap 30 detik; R4 tidak mengalami decay otomatis.

Rule ini adalah heuristik prototipe, bukan deteksi ransomware berbasis machine learning dan bukan jaminan semua ransomware akan terdeteksi.

---

## 4. Persyaratan

### Untuk demo backend + dashboard
- Git
- Docker Engine atau Docker Desktop
- Docker Compose v2 (perintah docker compose)
- Port lokal 8000 dan 8080 tersedia
- Koneksi internet saat pertama kali build image/dependency

### Untuk menjalankan endpoint agent
- Python 3.11 atau lebih baru
- VM/host lab terpisah yang disposable sangat disarankan
- Koneksi IP dari endpoint menuju backend
- Folder uji khusus yang tidak berisi data pribadi/produksi

Dashboard sudah dibuild di image Docker. Node.js hanya diperlukan bila mengembangkan dashboard secara langsung.

## 5. Cara tercepat menjalankan demo (tanpa VM)

Cara ini cocok untuk memeriksa dashboard, API, penyimpanan event dan tampilan skenario sintetis. Cara ini **belum** menguji agent pada endpoint terpisah.

1. Clone repo dan masuk ke folder:
   ~~~bash
   git clone https://github.com/SEKAT-Cyber-Team/SEKAT.git
   cd SEKAT
   ~~~

2. Jalankan skrip demo:
   ~~~bash
   bash scripts/demo-local.sh
   ~~~

   Jika file .env belum ada, skrip membuat dua API key acak dan berbeda, membatasi bind API ke 127.0.0.1, membangun container, menunggu health check, lalu mengirim enam event sintetis.

3. Buka dashboard: http://localhost:8080

4. Ambil nilai SEKAT_ADMIN_API_KEY dari file .env di root repository, lalu masukkan ke halaman login dashboard. Kunci dashboard disimpan di sessionStorage tab browser dan hilang saat sesi berakhir atau console dikunci.

5. Pastikan enam host demo dan event muncul. Data tersebut sintetis, bukan hasil pengamatan endpoint nyata.

Perintah operasional:
~~~bash
docker compose ps
docker compose logs -f backend
docker compose logs -f dashboard
docker compose down
~~~

docker compose down menghentikan container tetapi mempertahankan volume database. Untuk menghapus database demo beserta volume secara permanen:
~~~bash
docker compose down -v
~~~

## 6. Menjalankan simulator secara manual

Setelah backend berjalan, buka terminal di root repo.

Linux/macOS:
~~~bash
set -a
source .env
set +a

python3 -m pip install -r simulator/requirements.txt
python3 simulator/simulate.py --scenario normal --host-id demo-normal --key $SEKAT_AGENT_API_KEY
python3 simulator/simulate.py --scenario scan --host-id demo-scan --key $SEKAT_AGENT_API_KEY
python3 simulator/simulate.py --scenario file-burst --host-id demo-files --key $SEKAT_AGENT_API_KEY
python3 simulator/simulate.py --scenario canary --host-id demo-canary --key $SEKAT_AGENT_API_KEY
python3 simulator/simulate.py --scenario critical --host-id demo-critical --key $SEKAT_AGENT_API_KEY
python3 simulator/simulate.py --scenario audit --host-id demo-audit --key $SEKAT_AGENT_API_KEY
~~~

Simulator mengirim satu payload sintetis per perintah. Ia tidak membuat file uji, tidak menyentuh canary sungguhan, tidak memindai jaringan, dan tidak menjalankan ransomware.

---

## 7. Menjalankan endpoint agent di VM lab

**Jangan gunakan endpoint produksi atau laptop harian.** Gunakan VM disposable dengan jaringan Host-Only antara VM dan komputer yang menjalankan Docker. Hindari Bridged/public network untuk pengujian ini.

### A. Siapkan backend/controller

1. Pastikan demo dapat berjalan lebih dulu.
2. Temukan alamat IPv4 pada interface Host-Only komputer controller.
3. Edit .env pada root repository:
   - Set SEKAT_BIND_HOST ke IP interface Host-Only controller. Contoh IP: 192.168.56.1 (ganti dengan IP yang benar pada komputermu).
   - SEKAT_AUTO_ISOLATE=false
4. Pastikan firewall host hanya mengizinkan port TCP 8000 dari subnet Host-Only. Dashboard tetap terikat ke localhost port 8080.
5. Recreate container setelah mengubah bind address:
   ~~~bash
   docker compose up --build -d
   docker compose ps
   CONTROLLER_IP=192.168.56.1  # ganti dengan IP interface Host-Only controller\n   curl http://$CONTROLLER_IP:8000/health
   ~~~
   Jika shell belum memuat variabel .env, gunakan IP Host-Only secara langsung pada perintah curl. Jangan mengganti bind host menjadi 0.0.0.0 untuk demo.

### B. Siapkan VM endpoint

1. Clone repo ke VM lab dan masuk ke direktori agent:
   ~~~bash
   git clone https://github.com/SEKAT-Cyber-Team/SEKAT.git
   cd SEKAT/agent
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ~~~

2. Edit agent/.env:
   - Set SEKAT_API_URL ke alamat backend Host-Only, misalnya http://192.168.56.1:8000. Ganti IP contoh dengan alamat controller yang benar.
   - SEKAT_API_KEY=<nilai SEKAT_AGENT_API_KEY dari .env controller>
   - SEKAT_HOST_ID=nama-endpoint-lab-yang-unik
   - SEKAT_WATCH_PATHS=/tmp/sekat-lab
   - SEKAT_CANARY_PATH=/tmp/sekat-lab/SEKAT_CANARY.txt
   - SEKAT_SIMULATED_QUARANTINE=true

3. Buat folder dan marker aman:
   ~~~bash
   mkdir -p /tmp/sekat-lab
   printf 'SEKAT harmless canary marker\n' > /tmp/sekat-lab/SEKAT_CANARY.txt
   ~~~

4. Uji koneksi VM ke controller:
   ~~~bash
   curl http://192.168.56.1:8000/health  # ganti IP contoh dengan IP Host-Only controller
   ~~~

5. Muat konfigurasi dan jalankan agent:
   ~~~bash
   set -a
   source .env
   set +a
   python -m sekat_agent
   ~~~

6. Buka dashboard di komputer controller: http://localhost:8080. Endpoint akan muncul setelah heartbeat/event pertama diterima.

Agent hanya memantau folder yang ditentukan. Observasi koneksi bergantung pada izin OS; jika sistem menolak akses, agent mencatat warning dan melewati sampel. Jangan memperluas hak akses atau folder pantauan ke direktori pribadi hanya untuk menghilangkan warning.

### C. Uji file event yang aman

Di VM endpoint, buka terminal kedua dan lakukan:
~~~bash
printf 'harmless test data\n' > /tmp/sekat-lab/test-1.txt
for n in $(seq 1 35); do printf 'test %s\n' "$n" > "/tmp/sekat-lab/file-$n.txt"; done
printf 'marker touched\n' >> /tmp/sekat-lab/SEKAT_CANARY.txt
~~~

Lihat dashboard untuk event agent. Ambang R2 bergantung jumlah event filesystem yang benar-benar diterima watcher; satu operasi shell dapat menghasilkan lebih dari satu event OS.

### D. Uji Isolate/Release simulasi

1. Pilih endpoint agent yang sudah online.
2. Klik **Isolate**, konfirmasi peringatan simulasi.
3. Agent mem-poll command, mengubah flag internal simulasi, lalu mengirim acknowledgement.
4. Dashboard menampilkan isolated_simulated.
5. Klik **Release** untuk mengembalikan flag simulasi.
6. Pastikan jaringan, firewall dan interface VM tidak berubah.

Jika perintah tertahan di status Pending, periksa log agent dan backend. Jangan menganggap endpoint benar-benar terisolasi.

---

## 8. Konfigurasi penting

| Variabel | Fungsi | Default aman |
|---|---|---|
| SEKAT_AGENT_API_KEY | Kunci bersama untuk agent API | Placeholder; wajib diganti |
| SEKAT_ADMIN_API_KEY | Kunci dashboard/admin API | Placeholder; wajib diganti |
| SEKAT_DB_PATH | Path SQLite di container backend | /data/sekat.db |
| SEKAT_CORS_ORIGINS | Origin browser yang diizinkan | http://localhost:8080 |
| SEKAT_AUTO_ISOLATE | Antrean isolate otomatis untuk skor >=70 | false |
| SEKAT_BIND_HOST | Interface host untuk API port 8000 | 127.0.0.1 |
| SEKAT_API_URL | URL backend dari agent | http://127.0.0.1:8000 |
| SEKAT_WATCH_PATHS | Daftar folder pantauan dipisah koma | /tmp/sekat-lab |
| SEKAT_CANARY_PATH | Path marker canary | /tmp/sekat-lab/SEKAT_CANARY.txt |
| SEKAT_SIMULATED_QUARANTINE | Mengaktifkan respons simulasi pada agent | true |

Untuk lingkungan produksi, backend menolak placeholder, kunci yang lebih pendek dari 24 karakter, atau agent/admin key yang sama. Namun hal ini **tidak menjadikan sistem siap produksi**; kontrol keamanan tambahan tetap wajib.

Jangan pernah commit file .env, agent/.env, kredensial, database runtime, atau data endpoint ke Git.

## 9. API ringkas

Agent menggunakan header X-API-Key; dashboard menggunakan X-Admin-Key.

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | /health | Health backend (tanpa autentikasi) |
| POST | /api/events | Kirim event agent |
| GET | /api/commands?host=ID | Poll perintah untuk host |
| POST | /api/commands/ack | Acknowledge perintah; host_id wajib cocok |
| GET | /api/hosts | Daftar endpoint |
| GET | /api/events?host=ID&limit=50 | Riwayat event |
| POST | /api/hosts/{host_id}/commands | Antrekan isolate/release simulasi |
| GET | /api/settings | Baca konfigurasi mode |

Dokumentasi lengkap: docs/api.md.

## 10. Menjalankan tes otomatis

Dari root repository:
~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
(cd backend && PYTHONPATH=. pytest -q)

python -m pip install -r agent/requirements.txt
(cd agent && PYTHONPATH=. pytest -q)

python audit/check_config.py
(cd dashboard && npm install && npm run build)

cp .env.example .env
docker compose config --quiet
docker compose build
~~~

GitHub Actions menjalankan tes backend, tes agent, build dashboard, pemeriksaan konfigurasi, serta validasi/build Docker pada push dan pull request.

**Makna status hijau CI:** kode yang diuji lulus tes otomatis dan image dapat dibangun di runner GitHub. Itu tidak membuktikan runtime pada Parrot OS/VM lokal, konektivitas Host-Only, atau perilaku endpoint di semua sistem operasi.

Checklist pengujian manual dan kriteria penerimaan: docs/testing-plan.md.

## 11. Troubleshooting

| Gejala | Pemeriksaan |
|---|---|
| Dashboard tidak terbuka | docker compose ps, pastikan port 8080 belum dipakai |
| API health gagal | docker compose logs --tail=100 backend; cek .env dan bind IP |
| Dashboard menolak key | Gunakan SEKAT_ADMIN_API_KEY, bukan agent key; lock console lalu login lagi |
| Agent gagal konek | Cek SEKAT_API_URL, IP Host-Only, firewall TCP 8000, dan agent key |
| Endpoint tidak tampil | Tunggu heartbeat, cek log agent, pastikan SEKAT_HOST_ID unik |
| R2 tidak muncul | Pastikan folder yang diubah berada di SEKAT_WATCH_PATHS; cek watcher aktif |
| R3 tidak muncul | Path canary harus sama persis dengan SEKAT_CANARY_PATH; restart agent untuk reset state canary |
| Command Pending | Agent harus aktif, memiliki koneksi ke backend, dan menggunakan host ID yang sama |
| Network observation warning | OS membatasi akses psutil; deteksi koneksi dapat terlewat dan tidak boleh dianggap lengkap |

Dokumentasi tambahan:
- Arsitektur: docs/architecture.md
- Setup agent VM: docs/agent-setup.md
- Testing plan: docs/testing-plan.md
- Demo script: docs/demo-script.md
- Security notes & threat model: SECURITY.md
- Submission pack: submission/README.md

## 12. Batasan dan status kesiapan

Hal-hal yang belum diimplementasikan atau belum dibuktikan:
- Tidak ada adapter karantina jaringan sungguhan.
- Agent menggunakan satu shared API key untuk semua endpoint; host ID adalah identifier, bukan identitas kriptografis endpoint. Karena itu, prototipe ini harus dibatasi ke lab tepercaya.
- Belum ada TLS, rate limiting, RBAC multi-user, enrollment/per-agent credential, secret rotation otomatis, atau security monitoring produksi.
- SQLite dan satu backend cocok untuk demo/single-node, bukan high availability.
- State detector agent disimpan di memori dan reset ketika agent restart.
- R1–R4 adalah heuristik awal; false positive/negative mungkin terjadi.
- Runtime manual pada Parrot OS dan VM target harus dilakukan sebelum mengklaim pengujian endpoint selesai.

**Kesimpulan:** SEKAT siap untuk automated CI checks dan demo sintetis lokal. Pengujian endpoint nyata dalam lab masih membutuhkan validasi manual sesuai docs/testing-plan.md. Jangan gunakan sebagai perlindungan aktif pada jaringan produksi.

---
Dibangun oleh **SEKAT-Cyber-Team** sebagai prototipe defensif untuk eksperimen dan demonstrasi di laboratorium terisolasi.
