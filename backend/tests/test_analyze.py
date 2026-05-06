import os
import tempfile

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_returns_core_analysis_fields():
    response = client.post(
        "/analyze",
        files={"video": ("test-shot.mp4", b"smoke-test-video-bytes", "video/mp4")},
    )

    assert response.status_code == 200
    data = response.json()
    metric_names = {metric["name"] for metric in data["metrics"]}

    assert data["ok"] is True
    assert data["analysis_mode"] == "placeholder"
    assert data["source"] == "rules_placeholder"
    assert "limitations" in data
    assert isinstance(data["limitations"], list)
    assert "knee_bend_depth" in metric_names
    assert "drift" in metric_names
    assert all("confidence" in metric for metric in data["metrics"])
    assert "fixes" in data
    assert isinstance(data["fixes"], list)
    assert "notes" in data
    assert isinstance(data["notes"], list)


def make_synthetic_knee_bend_video_bytes():
    tmp = tempfile.NamedTemporaryFile(suffix=".avi", delete=False)
    tmp.close()

    writer = cv2.VideoWriter(
        tmp.name,
        cv2.VideoWriter_fourcc(*"MJPG"),
        5.0,
        (200, 200),
    )

    for offset in (0, 2, -2, 1, -1):
        frame = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.circle(frame, (100, 40), 10, (255, 255, 255), -1)  # hip
        cv2.circle(frame, (130 + offset, 100), 10, (255, 255, 255), -1)  # knee
        cv2.circle(frame, (100, 160), 10, (255, 255, 255), -1)  # ankle
        writer.write(frame)

    writer.release()

    with open(tmp.name, "rb") as handle:
        payload = handle.read()

    os.remove(tmp.name)
    return payload


def test_analyze_can_use_real_knee_bend_path(monkeypatch):
    monkeypatch.delenv("ANALYSIS_FORCE_PLACEHOLDER", raising=False)

    response = client.post(
        "/analyze",
        files={"video": ("synthetic-knee-bend.avi", make_synthetic_knee_bend_video_bytes(), "video/x-msvideo")},
    )

    assert response.status_code == 200
    data = response.json()
    knee_metric = next(metric for metric in data["metrics"] if metric["name"] == "knee_bend_depth")

    assert data["ok"] is True
    assert data["debug"]["knee_bend_path"] == "experimental_real"
    assert data["debug"]["pose_enabled"] is True
    assert knee_metric["confidence"] >= 0.55
    assert "estimated knee flexion" in knee_metric["units"]


def test_analyze_can_force_placeholder_fallback(monkeypatch):
    monkeypatch.setenv("ANALYSIS_FORCE_PLACEHOLDER", "1")

    response = client.post(
        "/analyze",
        files={"video": ("synthetic-knee-bend.avi", make_synthetic_knee_bend_video_bytes(), "video/x-msvideo")},
    )

    assert response.status_code == 200
    data = response.json()
    knee_metric = next(metric for metric in data["metrics"] if metric["name"] == "knee_bend_depth")

    assert data["debug"]["knee_bend_path"] == "placeholder"
    assert data["debug"]["pose_enabled"] is False
    assert "Forced placeholder mode" in data["debug"]["fallback_reason"]
    assert knee_metric["notes"] == "Placeholder metric (pose extraction not enabled in v0.1)."
