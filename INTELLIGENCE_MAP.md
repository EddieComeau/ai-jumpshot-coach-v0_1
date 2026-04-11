# INTELLIGENCE MAP

## System Shape

AI Jumpshot Coach is currently a local desktop application split into two runtime layers:
- backend: FastAPI service on `127.0.0.1:8000`
- frontend: Electron shell hosting a React app

## Layer Map

### Frontend Layer

Location:
- `frontend/src`
- `frontend/electron`

Responsibilities:
- collect user video input
- collect shot preferences and constraints
- call backend endpoints
- display backend responses
- show provider/connectivity state

Important files:
- `frontend/src/App.jsx`
- `frontend/src/api.js`
- `frontend/electron/main.cjs`
- `frontend/electron/preload.cjs`

### Backend API Layer

Location:
- `backend/app/main.py`
- `backend/app/schemas.py`

Responsibilities:
- expose health, analysis, chat, and status endpoints
- validate request and response shapes
- orchestrate analysis and coaching calls

### Analysis Layer

Location:
- `backend/app/analysis.py`

Responsibilities:
- manage uploaded video bytes
- produce bounded placeholder metrics
- derive simple rules-engine fixes

Current limitations:
- no pose extraction
- no frame-level analysis
- no persisted artifacts

### Coaching Layer

Location:
- `backend/app/ollama.py`
- `backend/app/main.py`

Responsibilities:
- build grounded prompts for Ollama
- expose Ollama connection status
- fall back to local rules text when needed

## Runtime Flow

### Analyze Flow

1. User selects a local video in the desktop UI.
2. Frontend posts multipart form data to `POST /analyze`.
3. Backend writes the upload to a temp file.
4. Backend generates placeholder metrics.
5. Rules engine derives up to 3 fixes plus notes.
6. Backend returns the response and removes the temp file.

### Chat Flow

1. User enters preferences and a coaching question.
2. Frontend sends message, preferences, and latest analysis to `POST /chat`.
3. Backend assembles grounded fallback context.
4. If provider mode allows, backend attempts Ollama generation.
5. If Ollama fails or is disabled, backend returns local fallback coaching text.

## Authority Boundaries

Current authority boundaries must stay clear:
- analysis output is the only metric authority
- rules engine may interpret metrics but must not invent new ones
- chat may explain and coach, but should not become a hidden scoring engine
- frontend is a presentation and input layer, not a source of decision truth
- continuity docs describe system state but do not override code reality
