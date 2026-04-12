# CHATGPT README

## Purpose

This document is the strategy truth for AI Jumpshot Coach. It defines what should happen next, what boundaries must be preserved, and how milestones should be framed before implementation work begins.

## Project Summary

AI Jumpshot Coach is a desktop-first basketball shot analysis MVP. The current product direction is to help a player upload a video, get bounded mechanics feedback, and ask follow-up coaching questions grounded in that analysis and the player's stated preferences.

## Current Milestone

### Milestone
M2: Analysis UI transformation

### Objective
Replace raw JSON analysis display with a structured, user-friendly results UI while preserving backend behavior.

### In Scope
- frontend-only presentation changes
- metric cards for `knee_bend_depth` and `drift`
- simple status labels and short coaching text
- top fixes from the existing backend response
- persistent placeholder analysis disclaimer
- continuity-doc updates after implementation

### Out Of Scope
- backend expansion beyond the current local MVP
- persistent user history
- hidden scoring or ranking systems
- ML-based shot evaluation
- autonomous recommendation loops
- analysis logic changes
- authority shifts where support layers become decision layers
- speculative intelligence layers not backed by implemented behavior

## Guardrails

Future milestones should preserve these rules unless explicitly changed:
- do not silently turn placeholder analysis into claimed real biomechanics
- do not add ML, hidden scoring, or confidence theater
- do not persist coaching conclusions or player state by default
- do not let chat invent metrics not present in analysis payloads
- do not expand scope across multiple unrelated layers in one milestone
- do not claim completion without local verification
- do not let roadmap docs overwrite implementation truth

## Recommended Workflow

Use this build loop for each slice:
1. ChatGPT defines one bounded milestone.
2. The milestone states objective, scope, non-goals, guardrails, likely files, verification, and success criteria.
3. Codex implements end-to-end.
4. Codex verifies locally.
5. Codex updates continuity docs.
6. Codex reports checkpoint state.

## Checkpoint Rule

Codex should continuously track and explicitly call out these three checkpoints whenever a recommended pause point is reached:
- ChatGPT checkpoint
- Git Push Checkpoint
- I need to check something myself checkpoint

Recommended checkpoint reporting means:
- ChatGPT checkpoint: call this out when the current slice is a clean architecture or milestone handoff point
- Git Push Checkpoint: call this out when the current slice is coherent, verified enough for its scope, and cleanly describable as a push/commit unit
- I need to check something myself checkpoint: call this out when a human should manually review UX, behavior, wording, environment setup, or a product decision before proceeding

These checkpoints should be surfaced proactively, not only when requested.

## Next Milestone Candidates

Priority should stay on small MVP-strengthening slices. Good next steps would be:
- tighten API contracts and add lightweight backend tests
- make coaching responses more structured while still grounded in available analysis
- improve local run ergonomics and setup clarity
- refine the visual design of the results UI after manual review

## Milestone Framing Template

Every milestone should include:
- Objective
- What It Is Not
- Guardrails
- Likely Files
- Verification Requirements
- Success Criteria

## Continuity Reminder

After every implemented slice, update:
- `CHATGPT_README.md`
- `CODEX_README.md`
- `INTELLIGENCE_MAP.md`
- `DECISIONS.md`
