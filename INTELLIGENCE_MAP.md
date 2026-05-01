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
- if a brand-new optional metric cannot be measured for a clip, analysis may omit it or mark its limits explicitly; for replacement metrics such as `knee_bend_depth`, keep the metric present and surface low confidence plus explanatory notes

First real metric candidates:
- `knee_bend_depth`
  - measures the dip/load angle already represented by the current placeholder metric
  - high coaching value because it directly affects load, rhythm, and lift cues already present in the MVP
  - lowest integration difficulty because it preserves the current metric name, units style, and rules entry point
- `drift`
  - measures forward body travel during the shot
  - useful for balance and verticality coaching
  - moderate difficulty because reliable tracking of body center movement usually depends on more stable multi-frame detection than the first metric should require
- `release_angle`
  - measures ball or forearm release geometry in degrees
  - useful for arc and shot-shape discussion
  - higher difficulty because it likely needs clearer release-frame detection and a stronger upper-body landmark signal before it is trustworthy

Recommended first real metric:
- `knee_bend_depth`
  - best first step because it already exists in the contract, has immediate coaching value, and can transition from placeholder to real measurement without changing frontend expectations
  - real integration path: keep the same metric object shape and replace the placeholder `value` + `confidence` with measured outputs from the future analysis pipeline
  - rules impact: existing dip/load fixes can stay bounded to this metric without turning into a score; rules should keep generating narrow cues such as loading more smoothly or sitting into the hips more, not a composite grade
  - failure handling: if knee bend cannot be measured confidently, return low confidence or omit the metric and surface the limitation rather than inventing a fallback value

Real knee bend integration boundary:
- current placeholder location: `compute_stub_metrics()` creates the `knee_bend_depth` metric object
- future replacement location: the real measured `knee_bend_depth` should replace the placeholder metric inside the analysis layer before `rules_engine(metrics)` runs
- do not replace the value earlier than the analysis layer’s usable preprocessing outputs
- do not replace the value later in rules, chat, or frontend code

Pre-measurement boundary:
- uploaded video bytes enter `analyze_video_bytes()`
- future preprocessing may conceptually produce frames, landmarks, or keypoints
- those intermediate outputs are not metrics yet
- the swap boundary begins only when preprocessing outputs are stable enough to support a measurement function

Conceptual measurement boundary:
- `extract_frames(video_bytes or temp-path) -> frames`
- `detect_keypoints(frames) -> keypoints`
- `compute_knee_bend_depth(keypoints) -> value, confidence, notes`
- conceptual inputs:
  - extracted frames for detection
  - pose/keypoint data for measurement
- conceptual outputs:
  - `value`: normalized knee bend measurement
  - `confidence`: high-level trust estimate for that measurement
  - `notes`: optional explanation when visibility, angle, or clip quality limits the reading

Normalization boundary:
- raw geometry should be converted into the existing contract units before the metric object is emitted
- the normalized metric should continue using degree-style units consistent with the current placeholder representation
- confidence should remain a bounded per-metric value that reflects measurement quality, not overall shot quality

Internal orchestration sketch:
1. `analyze_video_bytes()` receives uploaded bytes and saves the temp file.
2. `extract_frames(...)` conceptually prepares frame data.
3. `detect_keypoints(...)` conceptually prepares body landmarks or keypoints.
4. `compute_knee_bend_depth(...)` conceptually derives raw knee bend measurement outputs.
5. `normalize_knee_bend_metric(...)` conceptually assembles the final contract-compatible metric object.
6. analysis assembles the full `metrics` list.
7. `rules_engine(metrics)` interprets the assembled metrics.
8. the existing `/analyze` response is returned unchanged at the top level.

Placeholder-to-real swap rule:
- placeholder logic remains the default until real measurement is available
- when real measurement is available, only these `knee_bend_depth` fields change:
  - `value`
  - `confidence`
  - optional `notes`
- the rest of the `/analyze` response remains unchanged so frontend, rules, and chat stay compatible

Integration-point failure handling:
- if the measurement step fails, the metric should still be returned
- use low confidence and explanatory notes instead of removing the metric
- downstream layers must not invent substitute values

Fallback layering:
- if frame extraction, keypoint detection, or knee bend measurement is unavailable, analysis should fall back inside the analysis layer before metrics are handed to `rules_engine(metrics)`
- fallback should return the current placeholder `knee_bend_depth` metric rather than forcing downstream layers to branch
- this keeps runtime behavior stable while allowing future real-measurement stages to be introduced incrementally

Extensibility pattern:
- future metrics such as `release_angle` should follow the same pattern:
  - reuse shared preprocessing helpers such as frame extraction and keypoint detection
  - add a metric-specific compute helper
  - normalize into the existing metric object structure
  - assemble into the same `metrics` list before rules interpretation
- this keeps measurement logic isolated per metric while sharing upstream analysis-layer stages

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
