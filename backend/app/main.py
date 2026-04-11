import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .analysis import analyze_video_bytes
from .ollama import chat_with_ollama, get_ollama_status
from .schemas import AnalyzeResponse, ChatRequest, ChatResponse

app = FastAPI(title="AI Jumpshot Coach v0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True, "service": "ai-jumpshot-coach", "version": "0.1"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(video: UploadFile = File(...)):
    video_bytes = await video.read()
    return analyze_video_bytes(video_bytes, video.filename or "upload.mp4")


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    chat_provider_raw = os.getenv("CHAT_PROVIDER", "mesh").lower()
    # Backward compatibility: "stub" is now called "rules".
    chat_provider = "rules" if chat_provider_raw == "stub" else chat_provider_raw
    use_ollama = chat_provider in {"mesh", "ollama"}

    reply_lines = [
        "For v0.1, coach chat is rules-first and analysis-grounded.",
        "I tailor cues to your shot preferences and constraints, not one universal form.",
        "Upload a clip and run Analyze; then I can explain knee bend and drift in your style.",
    ]

    if req.preferences:
        prefs = req.preferences
        if prefs.shot_style:
            reply_lines.append(f"Shot style noted: {prefs.shot_style}.")
        if prefs.do_not_change:
            reply_lines.append(f"Locked mechanics (won't force changes): {', '.join(prefs.do_not_change)}.")
        if prefs.focus_areas:
            reply_lines.append(f"Priority focus: {', '.join(prefs.focus_areas)}.")
        if prefs.physical_constraints:
            reply_lines.append(f"Physical constraints considered: {', '.join(prefs.physical_constraints)}.")
        if prefs.environment_notes:
            reply_lines.append(f"Environment context: {', '.join(prefs.environment_notes)}.")

    if req.last_analysis and "metrics" in req.last_analysis:
        reply_lines.append("I see a recent analysis. I can rank fixes while preserving your preferred mechanics.")

    if use_ollama:
        payload = req.model_dump()
        payload["fallback_context"] = reply_lines
        try:
            llm_reply = chat_with_ollama(payload)
            return ChatResponse(ok=True, reply=llm_reply)
        except RuntimeError as exc:
            reply_lines.append(f"Ollama unavailable, using local fallback: {exc}")

    reply_lines.append(f"You said: {req.message}")
    return ChatResponse(ok=True, reply="\n".join(reply_lines))


@app.get("/chat/status")
def chat_status():
    provider_raw = os.getenv("CHAT_PROVIDER", "mesh").lower()
    # Backward compatibility: "stub" is now called "rules".
    provider = "rules" if provider_raw == "stub" else provider_raw

    status = {
        "ok": True,
        "provider": provider,
        "fallback_enabled": True,
    }

    if provider in {"mesh", "ollama"}:
        status["ollama"] = get_ollama_status()
    else:
        status["ollama"] = {
            "connected": False,
            "model_available": False,
            "note": "Set CHAT_PROVIDER=mesh (default) to enable Ollama + fallback mode.",
        }

    return status
