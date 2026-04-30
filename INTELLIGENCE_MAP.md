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
- display structured shot analysis results from backend responses
- display structured chat response sections without changing backend wording
- display backend health responses
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
- mark the response contract with `analysis_mode`, `source`, `limitations`, and per-metric `confidence`
- derive simple rules-engine fixes
- preserve measurement authority inside the analysis layer so future real pose/video extraction plugs in here instead of moving into chat or frontend code

Current limitations:
- no pose extraction
- no frame-level analysis
- no persisted artifacts
- current metric values are deterministic placeholders, not validated biomechanics

Future real-analysis interface plan:
- input boundary: uploaded video bytes continue entering through `POST /analyze` and are handed to `backend/app/analysis.py`
- preprocessing stage: future frame extraction, tracking, or detection should happen inside the analysis layer before any metric is emitted
- measurement stage: pose/video signals should be converted into bounded measurements before rules or chat see them
- normalization stage: every returned metric should keep the existing structure of `name`, `value`, `units`, `confidence`, and optional `notes`
- interpretation stage: rules may interpret normalized metrics, but they must not create missing measurements
- response stage: `/analyze` should keep returning the current top-level contract so the frontend can keep rendering without an initial redesign

Future metric expansion model:
- new metrics such as release angle, elbow alignment, or timing should be added as additional metric objects in the existing `metrics` list
- placeholder metrics should be replaceable by real measurements, not removed as a concept from the contract
- each metric should carry its own confidence and optional notes so partial or low-trust measurements stay explicit
- if a metric cannot be measured for a clip, analysis should omit that metric or mark its limits in `notes`/`limitations` rather than letting downstream layers infer it

Partial-data handling plan:
- poor video quality, occlusion, or short clips should still produce a valid `/analyze` response when possible
- low-confidence or missing measurements should be surfaced through metric `confidence`, metric `notes`, and top-level `limitations`
- chat and rules must stay grounded in only the metrics that actually appear in analysis output

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
7. Frontend presents the existing response as metric cards, top fixes, notes, and a placeholder disclaimer.

Future staged model:
1. Input: uploaded video bytes enter the analysis layer.
2. Preprocessing: optional future frame extraction / detection runs inside analysis.
3. Measurement extraction: raw pose/video signals become candidate measurements.
4. Metric normalization: candidate measurements are emitted as contract-compatible metric objects.
5. Rules interpretation: the rules layer interprets returned metrics into bounded fixes and notes.
6. Presentation: frontend and chat explain returned analysis without creating new measurement truth.

### Chat Flow

1. User enters preferences and a coaching question.
2. Frontend sends message, preferences, and latest analysis to `POST /chat`.
3. Backend assembles grounded fallback context.
4. If provider mode allows, backend attempts Ollama generation.
5. If Ollama fails or is disabled, backend returns local fallback coaching text.
6. Frontend presents the returned chat text as readable sections with analysis/preference context indicators and a limited-analysis disclaimer.

## Authority Boundaries

Current authority boundaries must stay clear:
- analysis output is the only metric authority
- future pose extraction should replace or extend `backend/app/analysis.py` outputs, not move measurement authority into chat or frontend code
- rules engine may interpret metrics but must not invent new ones
- chat may explain and coach, but should not become a hidden scoring engine
- frontend is a presentation and input layer, not a source of decision truth
- frontend can format status labels for readability, but backend analysis remains the data source
- frontend can group chat text for readability, but must preserve backend response wording and meaning
- frontend must not manufacture metrics, confidence, or analysis conclusions that are absent from `/analyze`
- continuity docs describe system state but do not override code reality
