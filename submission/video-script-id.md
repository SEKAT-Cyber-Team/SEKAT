# Naskah Video SEKAT (Bahasa Indonesia)

Target short explainer: 60-90 seconds. Official video limit: 10 minutes.

1. Pembuka — SEKAT adalah prototype defensif kategori Penangkalan untuk deteksi dini perilaku yang berpotensi menyerupai aktivitas ransomware pada endpoint lab.
2. Masalah — Perubahan file dalam jumlah besar dan koneksi antar-endpoint yang tidak biasa dapat menjadi sinyal awal yang perlu diperiksa.
3. Arsitektur — Agent berjalan pada endpoint VM. Backend FastAPI dan SQLite berjalan pada controller Parrot OS. Dashboard React menjadi antarmuka operator.
4. Deteksi — R1 mengamati tiga atau lebih peer IPv4 privat dalam 20 detik (+40). R2 mengamati 30 atau lebih event file dalam 10 detik (+35). R3 memberi +60 ketika canary tersentuh. R4 memberi +15 untuk temuan audit dari operator.
5. Risiko — Skor dikategorikan Normal (0-39), Waspada (40-69) dan Kritis (70-100).
6. Respons — Operator dapat mengirim isolate/release. Agent mengambil command dan mengirim acknowledgement. Pada MVP ini, containment masih simulasi.
7. Batas keamanan — Tidak ada malware aktif, mass encryption, firewall modification atau pemutusan interface. Skenario demo memakai telemetry sintetis.
8. Penutup — Automated tests, dashboard build, Compose validation dan image build telah lolos CI. Validasi manual pada VM terisolasi masih menjadi langkah berikutnya.

## On-screen disclaimer
Synthetic telemetry | Simulated containment | Isolated lab prototype

## Recording checklist
- Hide API keys, tokens, terminal secrets and personal data.
- Do not claim real network isolation.
- If recording a live demo, use the dedicated lab folder and isolated host-only network.
- Check every displayed label and score before uploading.