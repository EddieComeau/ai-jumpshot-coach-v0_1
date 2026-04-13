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
