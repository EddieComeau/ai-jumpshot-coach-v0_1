import os
import tempfile
from typing import Dict, Any, List, Tuple


ANALYSIS_MODE = "placeholder"
ANALYSIS_SOURCE = "rules_placeholder"
ANALYSIS_LIMITATIONS = [
    "Pose extraction is not enabled in v0.1.",
    "Metric values are deterministic placeholder signals, not validated biomechanics.",
    "Rules may interpret returned metrics but must not create measurements that are absent from analysis.",
]


# MVP NOTE:
# - Kept runnable with zero heavy CV dependencies.
# - Real pose extraction can be added later in this module.

def save_upload_to_temp(contents: bytes, filename: str) -> str:
    suffix = os.path.splitext(filename)[-1] or ".mp4"
    fd, path = tempfile.mkstemp(prefix="upload_", suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(contents)
    return path


def compute_stub_metrics() -> List[Dict[str, Any]]:
    # Two MVP metrics: knee bend + drift (placeholder values)
    return [
        {
            "name": "knee_bend_depth",
            "value": 38.0,
            "units": "deg (approx knee angle at dip)",
            "confidence": 0.35,
            "notes": "Placeholder metric (pose extraction not enabled in v0.1).",
        },
        {
            "name": "drift",
            "value": 0.22,
            "units": "body widths forward",
            "confidence": 0.35,
            "notes": "Placeholder metric (pose extraction not enabled in v0.1).",
        },
    ]


def rules_engine(metrics: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    knee = next((m for m in metrics if m["name"] == "knee_bend_depth"), None)
    drift = next((m for m in metrics if m["name"] == "drift"), None)

    fixes: List[Dict[str, Any]] = []
    notes: List[str] = []

    if knee:
        if knee["value"] < 45:
            fixes.append(
                {
                    "issue": "Shallow dip / limited load",
                    "evidence": f"knee_bend_depth ~= {knee['value']} (below target load range)",
                    "cue": "Sit into your hips a bit more with smooth tempo.",
                    "drill": "Wall dip reps: 3x8 slow dips, 1s hold, rise.",
                }
            )
        else:
            notes.append("Knee bend appears adequate (from current metric).")

    if drift:
        if drift["value"] > 0.18:
            fixes.append(
                {
                    "issue": "Forward drift",
                    "evidence": f"drift ~= {drift['value']} body widths forward",
                    "cue": "Think up, not out; finish tall and stacked.",
                    "drill": "Tape-line jumps: land on/behind line, 5x5 makes.",
                }
            )
        else:
            notes.append("Drift appears controlled (from current metric).")

    notes.append("Positive: run completed with consistent metric output shape.")
    return fixes[:3], notes


def analyze_video_bytes(video_bytes: bytes, filename: str) -> Dict[str, Any]:
    path = save_upload_to_temp(video_bytes, filename)
    try:
        metrics = compute_stub_metrics()
        fixes, notes = rules_engine(metrics)
        return {
            "ok": True,
            "video_filename": filename,
            "analysis_mode": ANALYSIS_MODE,
            "source": ANALYSIS_SOURCE,
            "limitations": ANALYSIS_LIMITATIONS,
            "metrics": metrics,
            "fixes": fixes,
            "notes": notes,
            "debug": {"temp_path": path, "pose_enabled": False},
        }
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
