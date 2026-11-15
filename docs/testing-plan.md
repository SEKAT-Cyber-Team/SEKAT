# Test plan dan kriteria penerimaan

Dokumen ini memisahkan **tes otomatis**, **demo sintetis**, dan **pengujian runtime agent pada VM**. Ketiganya tidak boleh diklaim sebagai hal yang sama.

## 1. Tes otomatis (CI)

Perintah dari root repository:
~~~bash
(cd backend && python -m pip install -r requirements.txt && PYTHONPATH=. pytest -q)
(cd agent && python -m pip install -r requirements.txt && PYTHONPATH=. pytest -q)
python audit/check_config.py
(cd dashboard && npm install && npm run build)
cp .env.example .env
docker compose config --quiet
docker compose build
~~~

GitHub Actions menjalankan lima job: backend, agent, dashboard, audit, containers. Hasil hijau berarti job yang tercantum selesai berhasil di runner GitHub; tidak berarti aplikasi telah dijalankan pada host/VM target.

## 2. Demo sintetis lokal

1. Jalankan bash scripts/demo-local.sh.
2. Pastikan GET /health menghasilkan status ok.
3. Login dashboard dengan admin key dari root .env.
4. Pastikan host/event sintetis terlihat.
5. Cocokkan skenario Normal, R1, R2, R3, Critical dan R4 dengan nilai yang diharapkan.
6. Antrean isolate/release melalui dashboard hanya dapat diuji sampai antrean pada demo simulator-only; untuk round-trip agent, jalankan agent terpisah.

## 3. Penerimaan agent VM (manual, wajib sebelum menyatakan runtime teruji)

- [ ] Backend dan dashboard berjalan tanpa crash.
- [ ] API terikat hanya ke localhost atau IP interface Host-Only yang spesifik.
- [ ] Firewall host membatasi TCP 8000 ke subnet Host-Only.
- [ ] VM dapat mengakses /health pada alamat controller.
- [ ] Agent berjalan dengan folder pantauan /tmp/sekat-lab saja.
- [ ] Heartbeat endpoint muncul di dashboard dalam waktu sekitar 30 detik.
- [ ] Event file aman terkirim ketika file uji dibuat/diubah di folder tersebut.
- [ ] Canary marker terdeteksi setelah marker disentuh; restart agent untuk mengulangi trigger satu kali.
- [ ] Event risk score dan daftar event terlihat di dashboard.
- [ ] Isolate command diterima agent, di-ack, dan state menjadi isolated_simulated.
- [ ] Release command diterima agent, di-ack, dan state menjadi released.
- [ ] Verifikasi OS: firewall, route, interface dan koneksi jaringan tidak berubah.
- [ ] VM dapat dihentikan/dihapus tanpa berdampak pada perangkat atau jaringan lain.

## 4. Negative/security checks

- [ ] Event tanpa agent key atau dengan key salah mendapat 401.
- [ ] Dashboard API tanpa admin key atau key salah mendapat 401.
- [ ] Rule tak dikenal, skor di luar 0–100, timestamp tanpa timezone, dan detail lebih dari 4096 byte ditolak.
- [ ] Host yang tidak cocok tidak dapat meng-ack command milik host lain.
- [ ] Command duplikat yang masih pending/delivered ditolak (409).
- [ ] Isolate pada host yang sudah isolated_simulated ditolak (409).
- [ ] Release pada host yang belum isolated_simulated ditolak (409).
- [ ] .env, agent/.env, database runtime, virtualenv dan node_modules tidak ada pada commit.
- [ ] Port 8000 tidak dapat diakses dari jaringan publik.
- [ ] Tidak ada pengujian malware atau tindakan destruktif.

## 5. Keterbatasan yang harus dicatat

- Satu shared agent key dipakai semua endpoint pada MVP ini. Host ID hanya pemisah data/perintah, bukan autentikasi perangkat yang kuat.
- Tidak ada TLS, rate limiting, RBAC, enrollment per endpoint atau rotasi key otomatis.
- Detector agent menyimpan state di memori; restart menghapus riwayat window/canary/risk agent.
- Network observation bergantung pada izin OS dan dapat melewatkan koneksi.
- SQLite adalah penyimpanan demo single-node.
- Isolate/release hanya simulasi dan tidak dapat melindungi endpoint nyata.
- Threshold R1–R4 adalah heuristik; false positive/negative mungkin terjadi.

## 6. Acceptance boundary

SEKAT dapat disebut **CI-passing** setelah semua job CI hijau. Sistem dapat disebut **local demo passing** setelah Compose, health, dashboard dan event sintetis berhasil berjalan pada mesin uji. Sistem hanya boleh disebut **agent VM runtime tested** setelah seluruh checklist VM di atas dijalankan dan bukti aktualnya disimpan. Ketiganya bukan status yang dapat saling menggantikan.
