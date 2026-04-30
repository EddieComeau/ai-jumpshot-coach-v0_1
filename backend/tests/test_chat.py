from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def sample_analysis():
    return {
        "ok": True,
        "video_filename": "test-shot.mp4",
        "analysis_mode": "placeholder",
        "source": "rules_placeholder",
        "limitations": [
            "Pose extraction is not enabled in v0.1.",
            "Metric values are deterministic placeholder signals, not validated biomechanics.",
        ],
        "metrics": [
            {
                "name": "knee_bend_depth",
                "value": 38.0,
                "units": "deg (approx knee angle at dip)",
                "confidence": 0.35,
            },
            {
                "name": "drift",
                "value": 0.22,
                "units": "body widths forward",
                "confidence": 0.35,
            },
        ],
        "fixes": [],
        "notes": [],
    }


def test_chat_without_analysis_returns_reply(monkeypatch):
    monkeypatch.setenv("CHAT_PROVIDER", "rules")

    response = client.post("/chat", json={"message": "What should I fix first?"})

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["reply"]


def test_chat_with_analysis_returns_reply(monkeypatch):
    monkeypatch.setenv("CHAT_PROVIDER", "rules")

    response = client.post(
        "/chat",
        json={
            "message": "What should I fix first?",
            "last_analysis": sample_analysis(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["reply"]


def test_chat_with_preferences_returns_reply(monkeypatch):
    monkeypatch.setenv("CHAT_PROVIDER", "rules")

    response = client.post(
        "/chat",
        json={
            "message": "What should I fix first?",
            "preferences": {
                "shot_style": "across-face at peak",
                "do_not_change": ["across-face release"],
                "focus_areas": ["consistency"],
                "physical_constraints": ["low jump height"],
                "environment_notes": ["double rim"],
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["reply"]


def test_chat_status_returns_provider(monkeypatch):
    monkeypatch.setenv("CHAT_PROVIDER", "rules")

    response = client.get("/chat/status")

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["provider"] in {"rules", "mesh", "ollama"}
