import os
import tempfile
from math import acos, degrees, sqrt
from typing import Dict, Any, List, Optional, Tuple

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover - exercised through fallback behavior
    cv2 = None


ANALYSIS_MODE = "placeholder"
ANALYSIS_SOURCE = "rules_placeholder"
ANALYSIS_LIMITATIONS = [
    "Production-ready pose extraction is not enabled in v0.1.",
    "knee_bend_depth may use an experimental single-metric extraction path and fall back to placeholder output when unavailable or unreliable.",
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
REAL_KNEE_BEND_CONFIDENCE_THRESHOLD = 0.55
REAL_KNEE_BEND_FRAME_LIMIT = 6


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


def should_force_placeholder() -> bool:
    return os.getenv("ANALYSIS_FORCE_PLACEHOLDER", "").strip().lower() in {"1", "true", "yes", "on"}


def extract_frames(video_path: str, max_frames: int = REAL_KNEE_BEND_FRAME_LIMIT) -> Tuple[List[Any], str]:
    if cv2 is None:
        return [], "OpenCV unavailable."

    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        return [], "Video could not be opened for analysis."

    try:
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        frames: List[Any] = []

        if frame_count > 0:
            sample_count = min(max_frames, frame_count)
            sample_indices = sorted({int((frame_count - 1) * idx / max(sample_count - 1, 1)) for idx in range(sample_count)})
            for frame_index in sample_indices:
                capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                ok, frame = capture.read()
                if ok and frame is not None:
                    frames.append(frame)
        else:
            while len(frames) < max_frames:
                ok, frame = capture.read()
                if not ok or frame is None:
                    break
                frames.append(frame)

        if not frames:
            return [], "No readable frames were found."

        return frames, ""
    finally:
        capture.release()


def detect_keypoints(frame: Any) -> Tuple[Dict[str, Tuple[int, int]], float, str]:
    if cv2 is None:
        return {}, 0.0, "OpenCV unavailable."

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    markers = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 20:
            continue
        moments = cv2.moments(contour)
        if not moments["m00"]:
            continue
        center_x = int(moments["m10"] / moments["m00"])
        center_y = int(moments["m01"] / moments["m00"])
        markers.append({"point": (center_x, center_y), "area": float(area)})

    if len(markers) < 3:
        return {}, 0.0, "Not enough landmark candidates were detected."

    selected = sorted(markers, key=lambda item: item["area"], reverse=True)[:3]
    selected.sort(key=lambda item: item["point"][1])
    hip, knee, ankle = [item["point"] for item in selected]

    if not (hip[1] < knee[1] < ankle[1]):
        return {}, 0.0, "Landmark ordering was not usable."

    mean_area = sum(item["area"] for item in selected) / 3.0
    confidence = min(0.95, 0.35 + (mean_area / 250.0))
    return {"hip": hip, "knee": knee, "ankle": ankle}, confidence, ""


def compute_knee_bend_depth(keypoints: Dict[str, Tuple[int, int]]) -> Tuple[float, str]:
    hip = keypoints["hip"]
    knee = keypoints["knee"]
    ankle = keypoints["ankle"]

    upper = (hip[0] - knee[0], hip[1] - knee[1])
    lower = (ankle[0] - knee[0], ankle[1] - knee[1])
    upper_mag = sqrt((upper[0] ** 2) + (upper[1] ** 2))
    lower_mag = sqrt((lower[0] ** 2) + (lower[1] ** 2))

    if upper_mag == 0 or lower_mag == 0:
        raise ValueError("Knee angle vectors were degenerate.")

    cos_theta = ((upper[0] * lower[0]) + (upper[1] * lower[1])) / (upper_mag * lower_mag)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    joint_angle = degrees(acos(cos_theta))
    knee_flexion = max(0.0, 180.0 - joint_angle)
    return knee_flexion, "Experimental single-leg landmark estimate."


def normalize_knee_bend_metric(value: float, confidence: float, notes: str) -> Dict[str, Any]:
    return {
        "name": "knee_bend_depth",
        "value": round(value, 1),
        "units": "deg (estimated knee flexion at dip)",
        "confidence": round(max(0.0, min(1.0, confidence)), 2),
        "notes": notes,
    }


def attempt_real_knee_bend_metric(video_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    frames, frame_note = extract_frames(video_path)
    if not frames:
        return {}, {
            "used": False,
            "reason": frame_note or "Frame extraction failed.",
        }

    best_measurement: Optional[Dict[str, Any]] = None

    for frame in frames:
        keypoints, landmark_confidence, landmark_note = detect_keypoints(frame)
        if not keypoints:
            continue

        try:
            value, measurement_note = compute_knee_bend_depth(keypoints)
        except ValueError:
            continue

        combined_confidence = max(0.0, min(0.95, landmark_confidence))
        notes = measurement_note if not landmark_note else f"{measurement_note} {landmark_note}".strip()
        candidate = normalize_knee_bend_metric(value, combined_confidence, notes)
        if best_measurement is None or candidate["confidence"] > best_measurement["confidence"]:
            best_measurement = candidate

    if not best_measurement:
        return {}, {
            "used": False,
            "reason": "No usable knee landmarks were detected.",
            "sampled_frames": len(frames),
        }

    if best_measurement["confidence"] < REAL_KNEE_BEND_CONFIDENCE_THRESHOLD:
        return {}, {
            "used": False,
            "reason": "Knee measurement confidence was below threshold.",
            "sampled_frames": len(frames),
            "candidate_confidence": best_measurement["confidence"],
        }

    return best_measurement, {
        "used": True,
        "sampled_frames": len(frames),
        "confidence": best_measurement["confidence"],
    }


def build_metrics(video_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    metrics = compute_stub_metrics()
    debug = {
        "pose_enabled": False,
        "knee_bend_path": "placeholder",
    }

    if should_force_placeholder():
        debug["fallback_reason"] = "Forced placeholder mode enabled."
        return metrics, debug

    real_knee_metric, real_debug = attempt_real_knee_bend_metric(video_path)
    if not real_knee_metric:
        debug.update(real_debug)
        return metrics, debug

    debug.update(real_debug)
    debug["pose_enabled"] = True
    debug["knee_bend_path"] = "experimental_real"
    updated_metrics = []
    for metric in metrics:
        if metric["name"] == "knee_bend_depth":
            updated_metrics.append(real_knee_metric)
        else:
            updated_metrics.append(metric)
    return updated_metrics, debug


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
        metrics, path_debug = build_metrics(path)
        fixes, notes = rules_engine(metrics)
        return {
            "ok": True,
            "video_filename": filename,
            **analysis_contract_metadata(),
            "metrics": metrics,
            "fixes": fixes,
            "notes": notes,
            "debug": {"temp_path": path, **path_debug},
        }
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
