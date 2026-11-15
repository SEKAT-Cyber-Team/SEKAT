# Agent setup — disposable lab VM

Dokumen ini menjelaskan menjalankan Python agent pada VM endpoint yang terpisah dari controller Docker. Jangan gunakan endpoint produksi atau laptop harian. Versi ini hanya mendukung **simulasi** perintah isolate/release.

## 1. Konfigurasi controller

1. Salin root .env.example menjadi .env.
2. Buat dua API key acak yang berbeda (minimal 24 karakter), lalu isi SEKAT_AGENT_API_KEY dan SEKAT_ADMIN_API_KEY. Jangan commit file .env.
3. Jika agent berjalan pada host yang sama, pertahankan SEKAT_BIND_HOST=127.0.0.1.
4. Jika agent berada di VM terpisah, cari IP komputer controller pada interface Host-Only. Isi SEKAT_BIND_HOST dengan IP interface tersebut secara spesifik. Jangan gunakan 0.0.0.0.
5. Izinkan port TCP 8000 hanya dari subnet Host-Only melalui firewall host. Dashboard tetap terikat ke localhost port 8080.
6. Recreate service setelah mengubah bind address:
   ~~~bash
   docker compose up --build -d
   docker compose ps
   CONTROLLER_IP=192.168.56.1  # ganti dengan IP Host-Only controller\n   curl http://$CONTROLLER_IP:8000/health
   ~~~
   Untuk bind lokal, gunakan curl http://127.0.0.1:8000/health. Untuk bind Host-Only, health check lokal harus memakai IP Host-Only itu, bukan 127.0.0.1.

## 2. Siapkan endpoint VM

1. Clone repository ke VM disposable dan instal Python 3.11+.
2. Buat virtual environment:
   ~~~bash
   git clone https://github.com/SEKAT-Cyber-Team/SEKAT.git
   cd SEKAT/agent
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ~~~
3. Edit agent/.env:
   - SEKAT_API_URL=http://192.168.56.1:8000  (contoh; ganti dengan IP Host-Only controller)
   - SEKAT_API_KEY=<nilai SEKAT_AGENT_API_KEY dari .env controller>
   - SEKAT_HOST_ID=<identifier unik endpoint>
   - SEKAT_WATCH_PATHS=/tmp/sekat-lab
   - SEKAT_CANARY_PATH=/tmp/sekat-lab/SEKAT_CANARY.txt
   - SEKAT_SIMULATED_QUARANTINE=true
4. Buat folder dan marker:
   ~~~bash
   mkdir -p /tmp/sekat-lab
   printf 'SEKAT harmless canary marker\n' > /tmp/sekat-lab/SEKAT_CANARY.txt
   ~~~
5. Pastikan controller dapat dijangkau:
   ~~~bash
   curl http://192.168.56.1:8000/health  # gunakan IP Host-Only controller yang benar
   ~~~
6. Jalankan agent:
   ~~~bash
   set -a
   source .env
   set +a
   python -m sekat_agent
   ~~~

## 3. Pemeriksaan

- Dashboard di komputer controller: http://localhost:8080.
- Masukkan SEKAT_ADMIN_API_KEY dari root .env.
- Tunggu heartbeat pertama, endpoint akan muncul jika event berhasil dikirim.
- Jalankan file test hanya di /tmp/sekat-lab untuk melihat R2/R3.
- Klik Isolate dan Release; konfirmasi status isolated_simulated dan released.

Agent hanya mengamati folder yang dikonfigurasi dan koneksi established yang terlihat oleh proses. OS dapat menolak akses network observation; jika demikian agent mencatat warning dan melewati sampel. Jangan menaikkan privilege atau memperluas scope ke direktori pribadi hanya untuk menghilangkan warning.

## 4. Batas keselamatan

SEKAT_SIMULATED_QUARANTINE=true membuat perintah hanya mengubah flag di memori agent dan mengirim acknowledgement. Tidak ada perubahan firewall, routing, interface, proses, atau layanan OS. Adapter containment sungguhan tidak tersedia.

Semua endpoint menggunakan shared agent API key pada MVP ini. Host ID bukan identitas endpoint yang kuat. Batasi jaringan pada lab tepercaya dan jangan mengekspos port API ke internet.
