import os
import tempfile
from typing import Dict, Any, List, Tuple


ANALYSIS_MODE = "placeholder"
ANALYSIS_SOURCE = "rules_placeholder"
ANALYSIS_LIMITATIONS = [
    "Pose extraction is not enabled in v0.1.",
    "Metric values are deterministic placeholder signals, not validated biomechanics.",
    "Rules may interpret returned metrics but must not create measurements that are absent from analysis.",
    "Future real pose or video measurements should replace or extend analysis outputs in this layer, not in chat or frontend code.",
]


# MVP NOTE:
# - Kept runnable with zero heavy CV dependencies.
# - Real pose extraction can be added later in this module.
# - Future real-analysis pipeline should stay in this layer:
#   1. ingest uploaded video bytes
#   2. preprocess frames / detections
#   3. extract measurements
#   4. normalize measurements into metric objects
#   5. return the existing analysis contract for rules + chat consumption
#
# Future internal helper sketch for real knee bend, conceptual only:
# - extract_frames(video_bytes or temp-path) -> frames
# - detect_keypoints(frames) -> keypoints
# - compute_knee_bend_depth(keypoints) -> value, confidence, notes
# - normalize_knee_bend_metric(value, confidence, notes) -> Metric-like dict
#
# Future orchestration order, conceptual only:
# 1. save uploaded video
# 2. attempt frame extraction
# 3. attempt keypoint detection
# 4. attempt knee bend measurement
# 5. normalize measured output into the existing metric contract
# 6. assemble metrics list
# 7. run rules_engine(metrics)
# 8. return the existing /analyze response shape
#
# Fallback layering:
# - if any real-measurement stage is unavailable or unreliable, keep using the
#   placeholder metric path for knee_bend_depth
# - fallback should happen inside analysis-layer metric assembly so rules, chat,
#   and frontend continue receiving a valid contract without special cases

def save_upload_to_temp(contents: bytes, filename: str) -> str:
    suffix = os.path.splitext(filename)[-1] or ".mp4"
    fd, path = tempfile.mkstemp(prefix="upload_", suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(contents)
    return path


def compute_stub_metrics() -> List[Dict[str, Any]]:
    # Two MVP metrics: knee bend + drift (placeholder values)
    # Future knee_bend_depth swap boundary:
    # - Placeholder knee_bend_depth is created here today.
    # - Real measurement should replace the knee_bend_depth metric object here,
    #   after preprocessing / keypoint detection outputs are usable, and before
    #   rules_engine(metrics) runs.
    # - Do not move measurement authority into rules_engine(), chat, or frontend code.
    #
    # Conceptual boundary only, not implemented here:
    # - extract_frames(video_bytes or temp-path) -> frames
    # - detect_keypoints(frames) -> keypoints
    # - compute_knee_bend_depth(keypoints) -> value, confidence, notes
    # - normalize_knee_bend_metric(value, confidence, notes) -> Metric-like dict
    #
    # Swap rule:
    # - keep metric name `knee_bend_depth`
    # - overwrite placeholder value, confidence, and optional notes only
    # - keep the surrounding /analyze contract unchanged
    #
    # Failure rule:
    # - if real measurement fails, keep returning the metric entry
    # - use low confidence plus explanatory notes
    # - do not invent a replacement value in downstream layers
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


def analysis_contract_metadata() -> Dict[str, Any]:
    return {
        "analysis_mode": ANALYSIS_MODE,
        "source": ANALYSIS_SOURCE,
        "limitations": ANALYSIS_LIMITATIONS,
    }


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
            **analysis_contract_metadata(),
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
