# CODEX README

## Purpose

This document is the implementation truth for AI Jumpshot Coach. It records what is actually built, what was verified locally, and the current checkpoint state.

## Current Implemented State

As of April 12, 2026, this repo contains:
- a FastAPI backend in `backend/app`
- an Electron + React frontend in `frontend`
- local video upload analysis with placeholder metrics
- a rules-engine that emits bounded coaching fixes
- a `/chat` endpoint that uses preferences and latest analysis
- optional Ollama-backed chat with fallback to local rules text
- a `/chat/status` endpoint for provider visibility
- a structured frontend `Shot Analysis` results section for existing analysis responses

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
- displays analysis results as metric cards, top fixes, notes, and a placeholder disclaimer
- displays health and chat responses as raw JSON/text
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
- `cd frontend && npm run build` passed
- analysis UI now renders structured metric cards for `knee_bend_depth` and `drift`
- top fixes and notes render from the existing backend response shape
- placeholder status is visible in the analysis UI

Not run in this pass:
- backend server startup
- frontend dev startup
- endpoint smoke tests

Reason:
- this milestone was frontend-only and did not change backend behavior

## Files Updated In This Pass

- `README.md`
- `CHATGPT_README.md`
- `CODEX_README.md`
- `INTELLIGENCE_MAP.md`
- `frontend/src/App.jsx`
- `frontend/src/styles.css`

## Checkpoint State

- ChatGPT checkpoint: yes, this is a clean handoff point after the analysis UI presentation slice
- Git Push Checkpoint: yes after the user reviews or accepts the UI slice; repo is connected to `origin/main` at `https://github.com/EddieComeau/ai-jumpshot-coach-v0_1.git`
- I need to check something myself checkpoint: yes, the user should manually review the desktop UI wording and visual feel because this milestone changed presentation

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
