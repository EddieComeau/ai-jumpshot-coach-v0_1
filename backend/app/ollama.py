import json
import os
from typing import Any, Dict
from urllib import request, error


def build_prompt(payload: Dict[str, Any]) -> str:
    message = payload.get("message", "")
    preferences = payload.get("preferences") or {}
    last_analysis = payload.get("last_analysis") or {}
    fallback_context = payload.get("fallback_context") or []

    instructions = (
        "You are a basketball jumpshot coach assistant. "
        "Use only the provided analysis and preferences. "
        "Do not invent metrics. "
        "If confidence is low or missing, acknowledge uncertainty. "
        "Keep response concise and practical."
    )

    return (
        f"{instructions}\n\n"
        f"Local rules context:\n{json.dumps(fallback_context, indent=2)}\n\n"
        f"User message:\n{message}\n\n"
        f"Preferences:\n{json.dumps(preferences, indent=2)}\n\n"
        f"Last analysis:\n{json.dumps(last_analysis, indent=2)}\n"
    )


def get_ollama_status() -> Dict[str, Any]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "5"))

    req = request.Request(
        url=f"{base_url}/api/tags",
        method="GET",
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw)
            models = parsed.get("models") or []
            model_names = [m.get("name", "") for m in models]
            model_available = any(name == model for name in model_names)
            return {
                "connected": True,
                "base_url": base_url,
                "model": model,
                "model_available": model_available,
            }
    except (error.URLError, error.HTTPError, json.JSONDecodeError, TimeoutError) as exc:
        return {
            "connected": False,
            "base_url": base_url,
            "model": model,
            "model_available": False,
            "error": str(exc),
        }


def chat_with_ollama(payload: Dict[str, Any]) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))

    body = {
        "model": model,
        "prompt": build_prompt(payload),
        "stream": False,
    }

    req = request.Request(
        url=f"{base_url}/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw)
            text = (parsed.get("response") or "").strip()
            if not text:
                raise ValueError("Ollama returned empty response.")
            return text
    except (error.URLError, error.HTTPError, json.JSONDecodeError, TimeoutError, ValueError) as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc
