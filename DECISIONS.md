# DECISIONS

## D1: Separate Strategy Truth From Implementation Truth

Decision:
- keep `CHATGPT_README.md` for roadmap and milestone intent
- keep `CODEX_README.md` for implemented and verified state

Why:
- prevents planning from drifting into assumed completion
- makes handoffs cleaner
- keeps milestone intent from being mistaken for shipped behavior

Must preserve:
- do not record unimplemented features as complete in implementation docs

## D2: Keep The MVP Local And Verifiable

Decision:
- keep the current architecture as a local FastAPI backend plus Electron/React desktop client

Why:
- it keeps iteration fast
- it reduces deployment complexity early
- it makes runtime verification straightforward

Must preserve:
- prefer small vertical slices over broad platform expansion

## D3: Placeholder Analysis Must Be Honest

Decision:
- current analysis remains explicitly placeholder until real pose extraction exists

Why:
- this avoids false confidence
- it keeps user-facing claims aligned with actual implementation

Must preserve:
- do not present stub metrics as validated biomechanics
- do not add fake sophistication through wording alone

## D4: Coaching Must Stay Grounded

Decision:
- coaching responses should depend on provided preferences and latest analysis
- Ollama is optional and must fall back safely

Why:
- preserves trust
- avoids brittle dependence on local model availability
- keeps the assistant aligned with actual evidence

Must preserve:
- chat must not invent unseen metrics
- chat must acknowledge limited confidence when analysis is limited

## D5: No Hidden Intelligence Layer

Decision:
- do not introduce ML scoring, persistence, autonomous learning loops, or silent authority layers unless explicitly requested

Why:
- keeps scope bounded
- preserves explainability
- prevents architecture drift during MVP development

Must preserve:
- recommendation logic should stay inspectable
- support layers must not quietly become authority layers

## D6: Continuity Docs Update With Each Phase

Decision:
- update continuity docs after each meaningful implementation slice

Why:
- preserves momentum across ChatGPT/Codex handoffs
- makes pause and resume easier
- creates reliable checkpoint awareness

Must preserve:
- docs should reflect the current system shape and latest verified status

## D7: Always Surface The Three Checkpoints

Decision:
- explicitly report `ChatGPT checkpoint`, `Git Push Checkpoint`, and `I need to check something myself checkpoint` when a slice reaches a recommended pause point

Why:
- it makes stopping points predictable
- it improves handoffs and push timing
- it reduces ambiguity about when human review is needed

Must preserve:
- checkpoint calls should be based on actual implementation and verification state
- if a checkpoint is not ready, say so directly instead of implying readiness

## D8: Analysis Contract Carries Measurement Authority

Decision:
- `/analyze` exposes explicit analysis metadata: `analysis_mode`, `source`, `limitations`, and per-metric `confidence`
- current values remain placeholder signals from `rules_placeholder`
- future real pose/video extraction should plug into the analysis layer and preserve analysis ownership of measurement truth

Why:
- prepares the response contract for future real pose/video measurements without adding pose extraction now
- keeps measurement truth inside the analysis layer
- prevents chat or frontend code from becoming hidden metric authorities

Must preserve:
- future real analysis should plug into `backend/app/analysis.py` and keep the response contract compatible where possible
- rules may interpret returned metrics but must not invent measurements
- chat may explain latest analysis and preferences but must not create unseen biomechanics data
- frontend may present and group analysis results, but it must not create new metrics, confidence values, or analysis conclusions
- low-confidence, partial, or failed measurements should be expressed through existing contract fields such as `confidence`, metric `notes`, and top-level `limitations`

## D9: Future Real Analysis Should Arrive As A Staged Plug-In

Decision:
- future real pose/video analysis should be documented as a staged pipeline inside the analysis layer:
  - input
  - preprocessing
  - measurement extraction
  - metric normalization
  - rules interpretation
- new measurable concepts should enter the system as additional metric objects using the existing metric structure

Why:
- makes the integration path for real analysis obvious without implementing CV now
- protects the frontend from unnecessary first-wave contract churn
- keeps rules and chat grounded in analysis-owned measurements

Must preserve:
- `POST /analyze` remains the only measurement authority boundary
- existing top-level response fields should remain valid when real measurements are introduced
- placeholder outputs should be replaceable by real metrics without moving authority into chat or frontend
- missing or low-confidence measurements must not be silently inferred by downstream layers

## D10: Start Real Measurement Work By Replacing An Existing Metric

Decision:
- the first real metric target should be `knee_bend_depth`
- the system should prefer replacing the current placeholder version of an existing metric before adding a brand-new measurable concept

Why:
- preserves contract compatibility with the current frontend and rules layer
- gives immediate coaching value with minimal architecture churn
- reduces risk compared with introducing a new metric that would need new rules and new UI assumptions at the same time

Must preserve:
- `knee_bend_depth` should continue using the existing metric object shape: `name`, `value`, `units`, `confidence`, and optional `notes`
- the placeholder-to-real transition should keep the metric name stable so frontend rendering and chat grounding remain compatible
- rules may generate bounded fixes from the measured metric, but they must not convert it into a hidden score
- if the metric cannot be measured reliably, analysis should return low confidence or explicit limitations instead of inventing a value
