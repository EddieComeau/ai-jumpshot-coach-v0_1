# AI Jumpshot Coach v0.1

Desktop MVP for basketball shot review with a local FastAPI backend and an Electron + React desktop client.

## Current Product Shape

The app currently includes:
- `POST /analyze` for placeholder jumpshot analysis from an uploaded video
- `POST /chat` for preference-aware coaching chat
- `GET /chat/status` for provider and Ollama availability checks
- `GET /health` for backend health checks

The desktop UI lets you:
- upload a video file
- run analysis
- enter player preferences and constraints
- send analysis-grounded coaching prompts and read structured coaching sections
- review structured shot analysis results, top fixes, and coaching notes

## Local Run

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash run.sh
```

Backend URL: `http://127.0.0.1:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

This starts Vite and Electron for local desktop development.

## Chat Provider Modes

Default mode is `mesh`:
- tries Ollama first
- falls back to local rules-based coaching if Ollama is unavailable

Mesh mode:

```bash
export CHAT_PROVIDER=mesh
export OLLAMA_MODEL=llama3.1:8b
# optional:
# export OLLAMA_BASE_URL=http://127.0.0.1:11434
# export OLLAMA_TIMEOUT_SECONDS=30
bash run.sh
```

Rules-only mode:

```bash
export CHAT_PROVIDER=rules
bash run.sh
```

Backward compatibility: `CHAT_PROVIDER=stub` still maps to `rules`.

Use `GET /chat/status` to confirm provider state and Ollama connectivity.

## Manual Smoke Test Checklist

Use this 5-10 minute checklist after starting the backend and frontend locally. The goal is to verify major MVP runtime paths without changing app behavior.

### 1. No Analysis State

1. Start the backend with the default `mesh` mode or `CHAT_PROVIDER=rules`.
2. Start the frontend with `npm run dev`.
3. Do not upload a video.
4. In Coach Chat, leave or enter a short message such as `What should I fix first?`.
5. Click `Send to /chat`.
6. Expected: the app does not crash, a coaching response appears, and the chat panel handles the missing analysis state gracefully.

### 2. Analysis Flow

1. Upload a local video file.
2. Click `Analyze`.
3. Expected: the `Shot Analysis` section renders metric cards for `Knee Bend Depth` and `Forward Drift`.
4. Expected: `Top Fixes`, `Coach Notes`, and the placeholder-analysis disclaimer are visible.

### 3. Chat With Analysis

1. Complete the analysis flow first.
2. Ask a coaching question such as `What should I fix first?`.
3. Click `Send to /chat`.
4. Expected: the chat response appears in structured sections, and `Based on latest shot analysis` is visible.

### 4. Preferences Applied

1. Enter at least one preference, such as a shot style or a do-not-change note.
2. Ask a coaching question.
3. Expected: the chat response reflects the preference where applicable, and `Adjusted for your preferences` is visible.

### 5. Rules Mode

1. Stop the backend if it is running.
2. Start it with rules mode:

```bash
cd backend
export CHAT_PROVIDER=rules
bash run.sh
```

3. Send a chat message from the frontend.
4. Expected: chat works without Ollama, provider status shows rules mode, and the structured chat UI still renders the response.

### 6. Mesh Mode

1. Stop the backend if it is running.
2. Start it with mesh mode:

```bash
cd backend
export CHAT_PROVIDER=mesh
bash run.sh
```

3. If Ollama is available, send a chat message and verify the response renders in the structured chat UI.
4. If Ollama is unavailable, send a chat message and verify the rules fallback response still renders without crashing.
5. Expected: mesh mode works with either Ollama output or fallback output, and `/chat/status` reflects the current connection state.

## Smoke Test Results

Latest verification: April 13, 2026

Runtime notes:
- Backend dependency environment was recreated with `python3 -m venv .venv` and `pip install -r requirements.txt`.
- Backend loopback server tests required local port access in the sandbox.
- Electron launch required unsetting `ELECTRON_RUN_AS_NODE` in this shell: `env -u ELECTRON_RUN_AS_NODE npm run dev`.
- No application code fixes were needed.

Results:
- PASS: No Analysis Chat. `CHAT_PROVIDER=rules` returned a coaching response without `last_analysis`.
- PASS: Analysis Flow. `POST /analyze` accepted a smoke-test upload and returned `knee_bend_depth`, `drift`, fixes, notes, and placeholder debug state.
- PASS: Chat With Analysis. `POST /chat` accepted `last_analysis` and returned analysis-aware fallback text.
- PASS: Preferences Applied. `POST /chat` accepted preferences and returned preference-aware lines including shot style, locked mechanics, focus area, physical constraint, and environment context.
- PASS: Rules Mode. `/chat/status` reported `provider: rules`, and chat worked without Ollama.
- PASS: Mesh Mode fallback. `/chat/status` reported `provider: mesh`; Ollama was unavailable locally, and chat returned the local fallback without crashing.
- SKIPPED: Live Ollama response. Ollama was not running at `http://127.0.0.1:11434`, so only mesh fallback was verified.
- PASS: Frontend dev server launch. Vite served the app at `http://127.0.0.1:5173/`.
- PASS: Electron dev app launch. `npm run dev` launched after unsetting `ELECTRON_RUN_AS_NODE`.
- PASS: Frontend production build. `cd frontend && npm run build` completed successfully.

## Current Analysis Behavior

`/analyze` currently returns:
- placeholder metrics for `knee_bend_depth` and `drift`
- up to 3 rules-engine fixes
- notes
- debug metadata

The frontend presents the analysis as user-friendly cards and lists while keeping the placeholder status visible.

This is intentionally a lightweight MVP. Real pose extraction is not enabled yet.

## Current Constraints

This repo does not currently include:
- auth
- cloud deployment
- persistence
- ball tracking
- make/miss detection
- ML scoring
- long-term feedback loops

## Build Loop Docs

This project now uses a split documentation model so planning and implementation status do not drift:
- `CHATGPT_README.md`: strategy truth
- `CODEX_README.md`: implementation truth
- `INTELLIGENCE_MAP.md`: system shape and boundaries
- `DECISIONS.md`: architectural decisions and guardrails

Use ChatGPT to define the next bounded milestone, and use Codex to implement, verify, and update continuity docs from the real codebase state.
