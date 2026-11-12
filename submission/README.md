# SEKAT — Submission Pack

Submission category: Penangkalan
Project: SEKAT — Sistem Early-warning & Karantina Anti-Tular Ransomware
Team: SEKAT-Cyber-Team

## Included project components
- Python endpoint agent, deterministic R1-R3 detector, scoped file observation and connection sampling.
- FastAPI backend with separate agent/admin API-key authentication and SQLite persistence.
- React dashboard for endpoint state, risk score, event history and response command queue.
- Safe synthetic telemetry simulator for Normal, scan, file-burst, canary, critical and audit scenarios.
- Docker Compose for backend and dashboard, plus GitHub Actions checks.
- Architecture, API, setup, test plan, demo script and video production notes.

## Evidence and honest status
| Evidence | Current status |
|---|---|
| Agent unit tests | Passed in GitHub Actions |
| Backend API tests | Passed in GitHub Actions |
| Dashboard production build | Passed in GitHub Actions |
| Compose configuration validation | Passed in GitHub Actions |
| Docker image build | Passed in GitHub Actions |
| Manual Parrot OS + endpoint VM run | Not yet performed by the team |
| Real network isolation | Not implemented; response is simulated only |

The generated presentation/video materials use synthetic data and illustrative UI previews. They are explanation assets, not a screen recording of a live endpoint VM test. Replace preview images with genuine screenshots if a live run is completed before submission.

## Submission checklist
- [ ] Provide a public project link judges can open (public repository or another public demo/download link).
- [ ] Ensure no .env, API keys, credentials, database files or personal data are committed.
- [ ] Thumbnail: 1200x630, JPG/PNG/WebP, at most 500 KB.
- [ ] Screenshots: no more than five images of the project interface.
- [ ] Video: uploaded to YouTube as Public or Unlisted; maximum 10 minutes.
- [ ] Explanation slides: include project, features, architecture and technologies.
- [ ] Declare pre-existing components and third-party libraries/tools as required by the rulebook.
- [ ] Verify every link from an incognito browser.
- [ ] Save the submission confirmation screenshot.

See criteria-matrix.md for the weighted evaluation mapping and video-script-id.md for the Indonesian narration.