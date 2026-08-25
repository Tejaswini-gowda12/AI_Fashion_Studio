import io
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List

# ── Configurable thresholds ────────────────────────────────────────────────────
MIN_WIDTH              = 512
MIN_HEIGHT             = 512
MIN_COVERAGE           = 0.70
LAPLACIAN_BLUR_THRESHOLD = 70.0
MIN_BRIGHTNESS         = 40.0
MAX_BRIGHTNESS         = 220.0


def analyze_image_quality(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Precise image-quality validation with per-check pass/fail status.

    Returns a dict with BOTH:
      • New structured fields: is_valid, quality_score (0-100), checks{}, user_guidance
      • Backward-compatible flat aliases: score (0-1), blur, lighting,
        fabric_coverage (float), min_resolution_passed, warning
        (used by older endpoint code and existing tests)
    """
    # ── 1. Open with Pillow to get resolution ────────────────────────────────
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        width, height = pil_img.size
    except Exception:
        _fail = {
            "is_valid": False,
            "quality_score": 0,
            "checks": {
                "resolution":      {"passed": False, "actual": "0 × 0 px",  "required": "minimum 512 × 512 px", "message": "Corrupted or unreadable image file."},
                "blur":            {"passed": False, "actual": "unknown",   "required": f"laplacian variance ≥ {LAPLACIAN_BLUR_THRESHOLD}", "message": "Could not inspect blur."},
                "lighting":        {"passed": False, "actual": "unknown",   "required": f"brightness {MIN_BRIGHTNESS}–{MAX_BRIGHTNESS}", "message": "Could not inspect lighting."},
                "fabric_coverage": {"passed": False, "actual": "0%",        "required": "at least 70%", "message": "Could not inspect coverage."},
            },
            "user_guidance": ["Upload a valid JPG, PNG, or WebP fabric image."],
            "width": 0, "height": 0,
            # ── backward-compat aliases ──
            "score": 0.0,
            "blur": "unknown",
            "lighting": "unknown",
            "fabric_coverage": 0.0,
            "min_resolution_passed": False,
            "warning": "Corrupted or unreadable image file.",
            "laplacian_var": 0.0,
            "brightness": 0.0,
        }
        return _fail

    # Convert image to numpy/gray for OpenCV checks
    file_bytes_np = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(file_bytes_np, cv2.IMREAD_COLOR)

    if img_cv is None:
        gray = np.array(pil_img.convert("L"))
    else:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # ── 2. Resolution Check ──────────────────────────────────────────────────
    width_ok  = width  >= MIN_WIDTH
    height_ok = height >= MIN_HEIGHT
    res_passed = width_ok and height_ok

    if res_passed:
        res_msg = "Image resolution meets the minimum 512 × 512 px requirement."
    elif not width_ok and not height_ok:
        res_msg = (
            f"Image width ({width} px) and height ({height} px) are too small. "
            "Upload an image at least 512 × 512 pixels."
        )
    elif not width_ok:
        res_msg = (
            f"Image width ({width} px) is too small. "
            "Upload an image at least 512 × 512 pixels."
        )
    else:
        res_msg = (
            f"Image height ({height} px) is too small. "
            "Upload an image at least 512 × 512 pixels."
        )

    resolution_check = {
        "passed":   res_passed,
        "actual":   f"{width} × {height} px",
        "required": "minimum 512 × 512 px",
        "message":  res_msg,
    }

    # ── 3. Blur Check ────────────────────────────────────────────────────────
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    blur_passed   = laplacian_var >= LAPLACIAN_BLUR_THRESHOLD

    if laplacian_var > 150.0:
        blur_status_label = "low blur (sharp)"
    elif laplacian_var >= LAPLACIAN_BLUR_THRESHOLD:
        blur_status_label = "medium blur"
    else:
        blur_status_label = "high blur"

    blur_check = {
        "passed":   blur_passed,
        "actual":   blur_status_label,
        "required": f"laplacian variance ≥ {LAPLACIAN_BLUR_THRESHOLD}",
        "message":  (
            "Image sharpness is acceptable."
            if blur_passed else
            "Image is too blurry. Hold the camera steady and capture a close-up with sharp focus."
        ),
    }

    # ── 4. Lighting Check ────────────────────────────────────────────────────
    avg_brightness   = float(np.mean(gray))
    lighting_passed  = MIN_BRIGHTNESS <= avg_brightness <= MAX_BRIGHTNESS

    if avg_brightness < MIN_BRIGHTNESS:
        lighting_label = "under-exposed"
        lighting_msg   = "Image is under-exposed / too dark. Use bright, even natural lighting."
    elif avg_brightness > MAX_BRIGHTNESS:
        lighting_label = "over-exposed"
        lighting_msg   = "Image is over-exposed / too bright. Avoid direct flash or intense glare."
    else:
        lighting_label = "good lighting"
        lighting_msg   = "Lighting is good."

    lighting_check = {
        "passed":   lighting_passed,
        "actual":   lighting_label,
        "required": f"brightness between {int(MIN_BRIGHTNESS)} and {int(MAX_BRIGHTNESS)}",
        "message":  lighting_msg,
    }

    # ── 5. Fabric Coverage Check ─────────────────────────────────────────────
    h, w     = gray.shape
    center   = gray[int(h * 0.15):int(h * 0.85), int(w * 0.15):int(w * 0.85)]
    edge_std = float(np.std(gray))
    ctr_std  = float(np.std(center))

    if edge_std == 0:
        coverage_ratio = 0.50
    else:
        coverage_ratio = min(1.0, max(0.40, (ctr_std / (edge_std + 1e-5)) * 0.85 + 0.15))

    coverage_pct    = int(round(coverage_ratio * 100))
    coverage_passed = coverage_ratio >= MIN_COVERAGE

    coverage_check = {
        "passed":   coverage_passed,
        "actual":   f"{coverage_pct}%",
        "required": "at least 70%",
        "message": (
            "Fabric occupies enough of the image."
            if coverage_passed else
            f"Fabric fills only {coverage_pct}% of the frame. Frame closer so fabric fills at least 70%."
        ),
    }

    # ── 6. Overall validity & quality score (0 – 100) ────────────────────────
    all_checks  = [resolution_check, blur_check, lighting_check, coverage_check]
    passed_count = sum(1 for c in all_checks if c["passed"])
    is_valid     = (passed_count == 4)

    # Weighted score: resolution 30 pts, blur 25, lighting 25, coverage 20
    quality_score = (
        (30 if res_passed      else max(0, int(30 * min(width, height) / MIN_WIDTH * 0.5)))
        + (25 if blur_passed   else max(0, int(25 * laplacian_var / LAPLACIAN_BLUR_THRESHOLD * 0.5)))
        + (25 if lighting_passed else max(0, int(25 * (1 - abs(avg_brightness - 130) / 130) * 0.5)))
        + (20 if coverage_passed else max(0, int(20 * coverage_ratio / MIN_COVERAGE * 0.5)))
    )
    quality_score = max(0, min(100, quality_score))

    # ── 7. User guidance — only for failed checks ─────────────────────────────
    guidance: List[str] = []
    if not res_passed:
        guidance.append("Upload a higher-resolution image, preferably 1024 × 1024 pixels.")
    if not blur_passed:
        guidance.append("Hold the camera steady; use macro or portrait mode for close-up focus.")
    if not lighting_passed:
        guidance.append("Use a close-up fabric photo in bright, even natural light.")
    if not coverage_passed:
        guidance.append("Ensure one fabric occupies most of the image (fill at least 70% of the frame).")
    if not guidance:
        guidance.append("Image quality is optimal for AI fabric feature extraction.")

    # ── 8. Build backward-compatible alias values ─────────────────────────────
    # 'warning': None if all pass; first failed check's message otherwise
    failed_messages = [c["message"] for c in all_checks if not c["passed"]]
    warning_compat  = failed_messages[0] if failed_messages else None

    # Legacy blur label: "low" / "medium" / "high"
    blur_compat = (
        "low"    if laplacian_var > 150.0 else
        "medium" if laplacian_var >= LAPLACIAN_BLUR_THRESHOLD else
        "high"
    )

    # Legacy lighting label: "good" / "under-exposed" / "over-exposed"
    lighting_compat = lighting_label

    return {
        # ── NEW structured fields ────────────────────────────────────────────
        "is_valid":      is_valid,
        "quality_score": quality_score,          # int 0-100
        "checks": {
            "resolution":      resolution_check,
            "blur":            blur_check,
            "lighting":        lighting_check,
            "fabric_coverage": coverage_check,
        },
        "user_guidance": guidance,

        # ── Raw measurements ─────────────────────────────────────────────────
        "width":          width,
        "height":         height,
        "laplacian_var":  round(laplacian_var, 1),
        "brightness":     round(avg_brightness, 1),

        # ── Backward-compatible flat aliases ─────────────────────────────────
        "score":               round(quality_score / 100, 2),    # float 0-1
        "blur":                blur_compat,                        # "low"/"medium"/"high"
        "lighting":            lighting_compat,                    # "good"/"under-exposed"/"over-exposed"
        "fabric_coverage":     round(coverage_ratio, 2),           # float 0-1
        "min_resolution_passed": res_passed,                       # bool (used by older tests)
        "warning":             warning_compat,                     # str | None
    }
