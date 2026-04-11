# CODEX README

## Purpose

This document is the implementation truth for AI Jumpshot Coach. It records what is actually built, what was verified locally, and the current checkpoint state.

## Current Implemented State

As of April 8, 2026, this repo contains:
- a FastAPI backend in `backend/app`
- an Electron + React frontend in `frontend`
- local video upload analysis with placeholder metrics
- a rules-engine that emits bounded coaching fixes
- a `/chat` endpoint that uses preferences and latest analysis
- optional Ollama-backed chat with fallback to local rules text
- a `/chat/status` endpoint for provider visibility

## Backend Reality

Implemented backend endpoints:
- `GET /health`
- `POST /analyze`
- `POST /chat`
- `GET /chat/status`

Current analysis implementation:
- saves uploaded video bytes to a temporary file
- computes placeholder metrics for `knee_bend_depth` and `drift`
- runs a simple rules engine
- returns metrics, fixes, notes, and debug metadata
- removes the temp file after processing

Current chat implementation:
- accepts a message, optional preferences, and optional last analysis
- builds a rules-grounded fallback response
- optionally calls Ollama in `mesh` or `ollama` mode
- falls back safely when Ollama is unavailable

## Frontend Reality

The frontend currently:
- lets the user select a local video file
- sends the file to `/analyze`
- collects player preference fields
- sends a chat prompt to `/chat`
- displays health, analysis, and chat responses largely as raw JSON/text
- checks chat provider status on load and on demand

## Verification Commands

Known local run commands:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash run.sh
```

```bash
cd frontend
npm install
npm run dev
```

## Verification Status

Verified in this pass:
- repository structure inspected
- backend and frontend implementation files reviewed
- continuity docs created from actual codebase state

Not run in this pass:
- backend server startup
- frontend dev startup
- endpoint smoke tests

Reason:
- the user request was documentation/process setup, and no explicit runtime verification was requested in this turn

## Files Updated In This Pass

- `README.md`
- `CHATGPT_README.md`
- `CODEX_README.md`
- `INTELLIGENCE_MAP.md`
- `DECISIONS.md`

## Checkpoint State

- ChatGPT checkpoint: yes, this is a clean handoff point for milestone planning
- Git push checkpoint: mostly yes from a docs/setup perspective, but this workspace is not currently a Git repo
- Need-you-to-check-something checkpoint: no blocking review needed for these docs alone

## Checkpoint Reporting Rule

Going forward, every meaningful slice should be evaluated against these three user-facing checkpoints:
- ChatGPT checkpoint
- Git Push Checkpoint
- I need to check something myself checkpoint

Recommended means:
- ChatGPT checkpoint: the slice is a clean stop for planning the next milestone
- Git Push Checkpoint: the slice is packaged cleanly enough to push for its current scope
- I need to check something myself checkpoint: there is a manual review or decision the human should make before we continue

If a checkpoint is not recommended yet, it should still be called out clearly as not ready.
