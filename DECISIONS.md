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
