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

Run the backend and frontend in separate terminal windows.

### Backend

From a fresh checkout:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash run.sh
```

Backend URL: `http://127.0.0.1:8000`

Check the backend:

```bash
curl http://127.0.0.1:8000/health
```

### Frontend

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run the desktop dev app:

```bash
npm run dev
```

This starts Vite and Electron for local desktop development.

If Electron launches as Node instead of Electron, use:

```bash
env -u ELECTRON_RUN_AS_NODE npm run dev
```

This is only needed when the shell has `ELECTRON_RUN_AS_NODE=1` set. In that state, Electron can fail with `TypeError: Cannot read properties of undefined (reading 'whenReady')` because the Electron runtime is being forced into Node mode.

Run a production frontend build:

```bash
npm run build
```

### Backend Tests

Run lightweight backend API contract tests:

```bash
cd backend
source .venv/bin/activate
pytest
```

## Verification

Use these quick checks to confirm the current MVP is healthy:

```bash
cd backend
.venv/bin/pytest
```

```bash
cd frontend
npm run build
```

For runtime behavior, follow the `Manual Smoke Test Checklist` below.

For Ollama mesh mode:

```bash
ollama serve
ollama list
```

Then run the backend with `CHAT_PROVIDER=mesh` and confirm:

```bash
curl http://127.0.0.1:8000/chat/status
```

Expected: `provider` is `mesh`, `ollama.connected` is `true`, and `model_available` is `true`. If Ollama is unavailable, mesh mode should fall back to the local rules response without crashing.

## Chat Provider Modes

The backend supports two main chat provider modes.

### Rules Mode

Rules mode does not attempt Ollama. Use this when you want the app to run without any local LLM dependency:

```bash
cd backend
source .venv/bin/activate
export CHAT_PROVIDER=rules
bash run.sh
```

Expected behavior:
- `/chat/status` reports `provider: rules`
- chat works without Ollama
- responses come from local fallback rules

### Mesh Mode

Mesh mode is the default. It tries Ollama first and falls back to local rules-based coaching if Ollama is unavailable:

```bash
cd backend
source .venv/bin/activate
export CHAT_PROVIDER=mesh
export OLLAMA_MODEL=llama3.1:8b
# optional:
# export OLLAMA_BASE_URL=http://127.0.0.1:11434
# export OLLAMA_TIMEOUT_SECONDS=30
bash run.sh
```

Backward compatibility: `CHAT_PROVIDER=stub` still maps to `rules`.

Use `GET /chat/status` to confirm provider state and Ollama connectivity.

## Common Issues

### Electron Starts As Node

Symptom:
- `npm run dev` fails with `TypeError: Cannot read properties of undefined (reading 'whenReady')`

Cause:
- the shell has `ELECTRON_RUN_AS_NODE=1` set

Fix:

```bash
cd frontend
env -u ELECTRON_RUN_AS_NODE npm run dev
```

### Ollama Is Not Running

Symptom:
- `/chat/status` reports `provider: mesh`, but `ollama.connected` is `false`
- chat response includes an Ollama unavailable fallback note

Expected behavior:
- mesh mode should still return a local fallback coaching response

Fix options:
- start Ollama and make sure the configured `OLLAMA_MODEL` is available
- or use `CHAT_PROVIDER=rules` to skip Ollama entirely

### Backend Is Not Running

Symptom:
- frontend health, analyze, chat, or chat status requests fail

Fix:

```bash
cd backend
source .venv/bin/activate
bash run.sh
```

Then confirm:

```bash
curl http://127.0.0.1:8000/health
```

## Manual Smoke Test Checklist

Use this 5-10 minute checklist after starting the backend and frontend locally. The goal is to verify major MVP runtime paths without changing app behavior.

### 1. No Analysis State

1. Start the backend with the default `mesh` mode or `CHAT_PROVIDER=rules`.
2. Start the frontend with `npm run dev`.
3. Do not upload a video.
4. In Coach Chat, leave or enter a short message such as `What should I fix first?`.
5. Click `Ask Coach`.
6. Expected: the app does not crash, a coaching response appears, and the chat panel handles the missing analysis state gracefully.

### 2. Analysis Flow

1. Upload a local video file.
2. Click `Analyze`.
3. Expected: the `Shot Analysis` section renders metric cards for `Knee Bend Depth` and `Forward Drift`.
4. Expected: `Top Fixes`, `Coach Notes`, and the placeholder-analysis disclaimer are visible.

### 3. Chat With Analysis

1. Complete the analysis flow first.
2. Ask a coaching question such as `What should I fix first?`.
3. Click `Ask Coach`.
4. Expected: the chat response appears in structured sections such as `Fix First` and `Why This Matters`, and `Using latest analysis` is visible.

### 4. Preferences Applied

1. Enter at least one preference, such as a shot style or a do-not-change note.
2. Ask a coaching question.
3. Expected: the chat response reflects the preference where applicable, and `Using your preferences` is visible.

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

## Ollama Verification

Latest verification: April 17, 2026

Environment:
- Ollama CLI available at `/usr/local/bin/ollama`
- Ollama server available at `http://127.0.0.1:11434`
- Model installed: `llama3.1:8b`

Results:
- PASS: `ollama list` showed `llama3.1:8b`.
- PASS: `GET /chat/status` in `CHAT_PROVIDER=mesh` reported `ollama.connected: true` and `model_available: true`.
- PASS: No-analysis chat returned a live Ollama response without fallback text.
- PASS: Chat with `last_analysis` returned a live Ollama response grounded in the provided placeholder metrics.
- PASS: Chat with preferences returned a live Ollama response that considered provided user context.
- PASS: Frontend production build still passed after verification.
- PASS: Backend API contract tests still passed after verification.
- PASS: Mesh fallback behavior was confirmed by running the backend with an unavailable `OLLAMA_BASE_URL`; chat returned the local fallback without crashing.

Notes:
- The fallback check used `OLLAMA_BASE_URL=http://127.0.0.1:59999` instead of stopping the user's Ollama service.
- No backend logic, prompt, UI, or feature changes were introduced for this verification.

## Frontend Clickthrough Review

Latest review: April 17, 2026

Live Ollama clickthrough results:
- PASS: Electron app launched with `env -u ELECTRON_RUN_AS_NODE npm run dev`.
- PASS: Backend ran in `CHAT_PROVIDER=mesh` with `llama3.1:8b`.
- PASS: `/chat/status` reported live Ollama connectivity.
- PASS: Analysis upload returned metric cards, top fixes, notes, and placeholder disclaimer data.
- PASS: No-analysis chat, chat with analysis, and chat with preferences returned live Ollama responses.
- PASS: Backend API contract tests still passed.
- PASS: Frontend production build still passed.

Targeted presentation fixes from review:
- Added a visible loading state while live Ollama responses are pending.
- Clarified mesh status labels as `Ollama active` or `Using fallback`.
- Improved chat section grouping so recommendation lines and numbered fixes stay under `Fix First`.
- Improved preference-related grouping for `Your Preferences`.

No backend behavior, prompt logic, response wording, or feature scope changed.

## Launch-Readiness Review

Latest review: April 29, 2026

Launch-readiness notes:
- README setup, verification, and Ollama instructions were checked against the current local run flow.
- Manual smoke checklist wording was aligned to the current frontend labels.
- The current UI labels to expect are `Ask Coach`, `Fix First`, `Other Cues`, `Why This Matters`, `Your Preferences`, `Ollama active`, `Using fallback`, `Using latest analysis`, and `Using your preferences`.
- The chat submit button was renamed from `Send to /chat` to `Ask Coach` so the desktop UI reads like a coaching action instead of an API call.
- No backend behavior, prompt logic, or feature changes were needed for this review.

## Current Analysis Behavior

`/analyze` currently returns:
- `analysis_mode: "placeholder"`
- `source: "rules_placeholder"`
- `limitations` describing the current lack of pose extraction, placeholder confidence, and the boundary that future measurements belong in the analysis layer
- placeholder metrics for `knee_bend_depth` and `drift`
- per-metric `confidence`
- up to 3 rules-engine fixes
- notes
- debug metadata

The frontend presents the analysis as user-friendly cards and lists while keeping the placeholder status visible.

This is intentionally a lightweight MVP. Real pose extraction is not enabled yet.

Contract boundary:
- the analysis layer owns metrics and whatever is currently known from the uploaded video
- the rules layer may interpret returned metrics, but it must not invent measurements
- chat may explain the latest analysis and user preferences, but it must not become a hidden scoring or biomechanics layer
- the frontend may present the payload clearly, but it must not create decision truth

Future pose or video extraction should plug into the backend analysis layer and continue returning known metrics through `/analyze` where possible. Real measurement authority should not move into chat or frontend code.

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
