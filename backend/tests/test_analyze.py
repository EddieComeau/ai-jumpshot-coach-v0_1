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
    assert "knee_bend_depth" in metric_names
    assert "drift" in metric_names
    assert "fixes" in data
    assert isinstance(data["fixes"], list)
    assert "notes" in data
    assert isinstance(data["notes"], list)
