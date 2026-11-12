# Video production

The presentation video is a separate production step. First run the application in the disposable lab, populate it with safe synthetic scenarios, and record the actual dashboard. Do not build the story around screens or features that do not exist.

## Recommended AI-assisted workflow: Remotion Agent Skills

Remotion is a React-based, code-driven video tool. Its official Agent Skills are designed for coding agents such as Codex, Claude Code, Cursor and Kimi Code. The skills teach the agent how to create compositions, animations, captions, preview and render.

Official resources:
- Remotion: https://github.com/remotion-dev/remotion
- Official Agent Skills: https://github.com/remotion-dev/skills
- Skills documentation: https://www.remotion.dev/docs/ai/skills

Install the skills in the environment where your coding agent runs:

```bash
npx skills add remotion-dev/skills
```

A separate video workspace keeps Remotion dependencies out of the SEKAT dashboard:

```bash
npx create-video@latest sekat-presentation
cd sekat-presentation
npm install
npx remotion studio
```

Ask the coding agent to use `/remotion-best-practices` and create a 60-90 second technical product demo for SEKAT. Require:
- Real screenshots or screen captures of the running SEKAT dashboard for product UI.
- An animated architecture flow: endpoint agent -> FastAPI -> SQLite -> dashboard -> simulated response.
- Clear R1-R4 explanations and risk score bands.
- Accurate labels: **synthetic telemetry** and **simulated quarantine**.
- No invented detections, fabricated performance numbers, fake live endpoints or claims of real network isolation.
- Readable Indonesian captions, consistent typography, clean transitions and a closing project/team credit.

Preview the composition in Remotion Studio, inspect every scene for spelling and factual accuracy, then render the MP4 when ready. Rendering is separate from the SEKAT runtime and is not required to run the security demo.

## Recording and editing checklist

1. Prepare the dashboard using separate demo host IDs and the normal, scan, file-burst, canary, critical and audit simulator scenarios.
2. Record at 1920x1080 with browser zoom at 100%; hide API keys and terminal secrets.
3. Capture the actual isolate/release command acknowledgement and state clearly that it is simulated.
4. Add captions, architecture overlays and voice-over; retain a visible disclaimer: **Synthetic telemetry | Simulated containment | Isolated lab demo**.
5. Review the rendered video frame by frame before submission.

Suggested run of show (4-5 minutes) is in `demo-script.md`.
