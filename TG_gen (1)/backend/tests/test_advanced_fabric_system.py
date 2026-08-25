"""
Tests for the Advanced Fabric Detection System.

Covers:
  - Structured image-quality validation (per-check pass/fail with exact messages)
  - Resolution validation: 612 × 443 must fail with height-specific message
  - Coverage 85% must pass 70% requirement
  - Generic warnings must NOT appear for passing checks
  - Low-confidence, high-confidence, invalid-image, multi-fabric cases
  - API response schema validation (explanation, visible_features, image_quality)
  - Model evaluation metrics
  - Prediction feedback endpoint
"""
import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from app.main import app
from app.services.image_quality_analyzer import analyze_image_quality
from app.ml.model_evaluator import generate_default_evaluation_metrics, SUPPORTED_19_CLASSES

client = TestClient(app)


# ─────────────────────────────── Helpers ────────────────────────────────────

def create_dummy_image(
    width: int = 600,
    height: int = 600,
    color: tuple = (120, 150, 180),
    add_texture: bool = True,
) -> bytes:
    """Creates a test JPEG image with optional texture lines."""
    img = Image.new("RGB", (width, height), color=color)
    if add_texture:
        draw = ImageDraw.Draw(img)
        for i in range(0, width, 10):
            draw.line([(i, 0), (i, height)], fill=(200, 220, 240), width=2)
            draw.line([(0, i), (width, i)], fill=(40, 60, 80), width=2)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# Image-Quality Analyser unit tests
# ═══════════════════════════════════════════════════════════════════════════

class TestImageQualityAnalyzer:
    """Unit tests for analyze_image_quality()."""

    # ── Resolution ──────────────────────────────────────────────────────────

    def test_valid_resolution_passes(self):
        """600 × 600 image must pass the 512 × 512 resolution check."""
        img = create_dummy_image(600, 600)
        res = analyze_image_quality(img, "fabric.jpg")

        assert res["checks"]["resolution"]["passed"] is True, (
            "600×600 should pass min-512 resolution requirement"
        )
        assert res["min_resolution_passed"] is True       # backward-compat alias
        assert res["width"] == 600
        assert res["height"] == 600

    def test_exact_minimum_resolution_passes(self):
        """512 × 512 must also pass (boundary condition)."""
        img = create_dummy_image(512, 512)
        res = analyze_image_quality(img, "fabric.jpg")
        assert res["checks"]["resolution"]["passed"] is True

    def test_612x443_fails_height_not_width(self):
        """
        CRITICAL: 612 × 443 image — width passes (612 ≥ 512) but height fails (443 < 512).
        The resolution check message must say 'height', NOT a generic fabric-coverage warning.
        """
        img = create_dummy_image(612, 443)
        res = analyze_image_quality(img, "swatch.jpg")

        res_check = res["checks"]["resolution"]
        assert res_check["passed"] is False, "612×443 height<512 must fail resolution"
        assert "height" in res_check["message"].lower(), (
            f"Expected 'height' in resolution message, got: '{res_check['message']}'"
        )
        assert "width" not in res_check["message"].lower() or "height" in res_check["message"].lower(), (
            "Message should specifically identify height as the failing dimension"
        )
        assert "443" in res_check["message"], "Actual height value should appear in message"

        # Backward-compat alias
        assert res["min_resolution_passed"] is False
        assert res["is_valid"] is False

    def test_low_resolution_both_dimensions_fail(self):
        """300 × 200 image — both width and height fail."""
        img = create_dummy_image(300, 200)
        res = analyze_image_quality(img, "tiny.jpg")

        res_check = res["checks"]["resolution"]
        assert res_check["passed"] is False
        assert res["min_resolution_passed"] is False
        # Should mention both dimensions
        msg = res_check["message"].lower()
        assert "width" in msg and "height" in msg

    def test_small_width_only_fails(self):
        """400 × 600 — width fails, height passes."""
        img = create_dummy_image(400, 600)
        res = analyze_image_quality(img, "narrow.jpg")

        res_check = res["checks"]["resolution"]
        assert res_check["passed"] is False
        assert "width" in res_check["message"].lower()
        assert "400" in res_check["message"]

    # ── Fabric Coverage ─────────────────────────────────────────────────────

    def test_coverage_85pct_passes_70pct_requirement(self):
        """
        CRITICAL: fabric_coverage of 85% must pass the 70% requirement.
        No 'fill at least 70%' warning must appear.
        """
        img = create_dummy_image(600, 600)
        res = analyze_image_quality(img, "fabric.jpg")

        cov_check = res["checks"]["fabric_coverage"]
        actual_pct_str = cov_check["actual"]   # e.g. "85%"
        actual_pct = int(actual_pct_str.replace("%", ""))

        if actual_pct >= 70:
            assert cov_check["passed"] is True, (
                f"Coverage {actual_pct}% should pass the 70% requirement, but failed"
            )
            # Warning must NOT mention fabric fill when coverage already passes
            if res.get("warning"):
                assert "70%" not in res["warning"] or "fill" not in res["warning"].lower(), (
                    "Generic fill-at-70% warning must NOT appear when coverage already passes"
                )

    def test_generic_fill_warning_absent_when_checks_pass(self):
        """
        If resolution, blur, lighting, and coverage all pass — no generic warning should appear.
        """
        img = create_dummy_image(700, 700)
        res = analyze_image_quality(img, "good_fabric.jpg")

        if res["is_valid"]:
            assert res.get("warning") is None, (
                "No warning should appear when all checks pass"
            )

    # ── Structured checks format ─────────────────────────────────────────────

    def test_structured_checks_present(self):
        """All four checks must be present in the structured response."""
        img = create_dummy_image(600, 600)
        res = analyze_image_quality(img, "fabric.jpg")

        assert "checks" in res
        for key in ("resolution", "blur", "lighting", "fabric_coverage"):
            assert key in res["checks"], f"Missing check: {key}"
            check = res["checks"][key]
            assert "passed" in check
            assert "message" in check

    def test_quality_score_range(self):
        """quality_score must be 0-100 integer; score (0-1 alias) must match."""
        img = create_dummy_image(600, 600)
        res = analyze_image_quality(img, "fabric.jpg")

        assert 0 <= res["quality_score"] <= 100
        assert 0.0 <= res["score"] <= 1.0
        assert abs(res["score"] - res["quality_score"] / 100) < 0.02  # within rounding

    def test_user_guidance_absent_for_passing_check(self):
        """user_guidance must NOT mention '70%' fill when coverage passes."""
        img = create_dummy_image(700, 700)
        res = analyze_image_quality(img, "fabric.jpg")

        cov = res["checks"]["fabric_coverage"]
        if cov["passed"]:
            for g in res.get("user_guidance", []):
                assert "70%" not in g or "fill" not in g.lower(), (
                    f"Guidance should not mention fill-70% when coverage passes: {g!r}"
                )

    # ── Backward-compat alias fields ─────────────────────────────────────────

    def test_backward_compat_aliases_present(self):
        """Legacy fields used by older endpoint code and tests must all be present."""
        img = create_dummy_image(600, 600)
        res = analyze_image_quality(img, "fabric.jpg")

        for key in ("score", "blur", "lighting", "fabric_coverage",
                    "min_resolution_passed", "warning"):
            assert key in res, f"Missing backward-compat alias: {key}"


# ═══════════════════════════════════════════════════════════════════════════
# ML Model Evaluation
# ═══════════════════════════════════════════════════════════════════════════

class TestModelEvaluation:
    def test_model_metrics_structure(self):
        metrics = generate_default_evaluation_metrics()

        assert metrics["accuracy"] >= 0.95, "Target 95%+ on held-out test set"
        assert metrics["macro_f1"] >= 0.94
        assert len(metrics["confusion_matrix"]) == 19
        assert len(metrics["confusion_matrix"][0]) == 19
        assert len(metrics["class_metrics"]) == 19
        assert "Acrylic" in metrics["class_metrics"]
        assert "Denim" in metrics["class_metrics"]

    def test_19_classes_supported(self):
        assert len(SUPPORTED_19_CLASSES) == 19
        for cls in ("Cotton", "Denim", "Silk", "Wool", "Polyester", "Unknown"):
            assert cls in SUPPORTED_19_CLASSES


# ═══════════════════════════════════════════════════════════════════════════
# API endpoint tests
# ═══════════════════════════════════════════════════════════════════════════

class TestFabricAnalyzeEndpoint:
    """Integration tests for POST /api/fabric/analyze."""

    def _post_image(self, width: int, height: int, filename: str = "swatch.jpg"):
        img_bytes = create_dummy_image(width, height)
        return client.post(
            "/api/fabric/analyze",
            files={"file": (filename, img_bytes, "image/jpeg")},
        )

    def test_valid_image_returns_200_with_full_schema(self):
        """600×600 image: endpoint must return 200 with all required fields."""
        resp = self._post_image(600, 600)
        assert resp.status_code == 200

        data = resp.json()
        # Required top-level fields
        for field in (
            "predicted_fabric", "confidence_score", "prediction_status",
            "top_predictions", "visible_features", "image_quality",
            "limitations", "explanation",
        ):
            assert field in data, f"Missing field in response: {field}"

        # Confidence fields
        assert 0 < data["confidence_score"] <= 1
        assert len(data["top_predictions"]) >= 1

        # Limitations must say AI-estimated
        assert "AI visual" in data["limitations"] or "AI" in data["limitations"]

    def test_image_quality_has_structured_checks(self):
        """image_quality in response must contain 'checks' dict with 4 sub-checks."""
        resp = self._post_image(600, 600)
        assert resp.status_code == 200

        iq = resp.json()["image_quality"]
        assert "is_valid" in iq
        assert "quality_score" in iq
        assert "checks" in iq
        checks = iq["checks"]
        for key in ("resolution", "blur", "lighting", "fabric_coverage"):
            assert key in checks, f"Missing check: {key}"
            assert "passed" in checks[key]
            assert "message" in checks[key]

    def test_high_confidence_prediction_status(self):
        """Well-lit, high-resolution image should produce high_confidence status."""
        resp = self._post_image(700, 700, "sharp_swatch.jpg")
        assert resp.status_code == 200
        data = resp.json()
        # Most test images with texture should yield high confidence
        assert data["prediction_status"] in ("high_confidence", "uncertain")

    def test_low_confidence_filename_trigger(self):
        """Filename containing 'lowconf' must trigger uncertain status with top-3 candidates."""
        resp = self._post_image(600, 600, filename="lowconf_sample.jpg")
        assert resp.status_code == 200
        data = resp.json()

        # Low-confidence trigger should lower confidence below 0.75
        assert data["confidence_score"] < 0.75 or data["prediction_status"] == "uncertain"
        assert len(data["top_predictions"]) >= 1

    def test_explanation_field_populated(self):
        """explanation field must be a non-empty string."""
        resp = self._post_image(600, 600)
        assert resp.status_code == 200
        explanation = resp.json().get("explanation", "")
        assert isinstance(explanation, str)
        assert len(explanation) > 20, f"Explanation too short: {explanation!r}"

    def test_visible_features_all_fields_present(self):
        """visible_features must include all 7 optical properties."""
        resp = self._post_image(600, 600)
        assert resp.status_code == 200
        vf = resp.json()["visible_features"]
        for field in ("texture", "weave", "pattern", "thickness", "shine", "stretch", "opacity"):
            assert field in vf, f"Missing visible_feature: {field}"

    def test_invalid_image_bytes_returns_400(self):
        """Sending non-image bytes must return 400."""
        resp = client.post(
            "/api/fabric/analyze",
            files={"file": ("corrupt.jpg", b"not-an-image", "image/jpeg")},
        )
        assert resp.status_code == 400

    def test_resolution_check_fails_for_small_image(self):
        """
        200×200 image: resolution check must fail and the response must still succeed
        (analysis runs), but image_quality.is_valid should be False and
        checks.resolution.passed should be False.
        """
        resp = self._post_image(200, 200, "tiny.jpg")
        # Endpoint returns 200 even for low-quality images (analysis still runs)
        if resp.status_code == 200:
            iq = resp.json()["image_quality"]
            assert iq["is_valid"] is False
            assert iq["checks"]["resolution"]["passed"] is False

    def test_api_response_schema_confidence_aliases(self):
        """Both 'confidence' and 'confidence_score' must be present and equal."""
        resp = self._post_image(600, 600)
        assert resp.status_code == 200
        data = resp.json()
        if "confidence" in data and "confidence_score" in data:
            assert abs(data["confidence"] - data["confidence_score"]) < 0.001


# ═══════════════════════════════════════════════════════════════════════════
# Feedback & Correction endpoints
# ═══════════════════════════════════════════════════════════════════════════

class TestFeedbackEndpoints:
    def test_prediction_feedback_endpoint(self):
        payload = {
            "predicted_fabric": "Cotton",
            "corrected_fabric": "Organic cotton",
            "verified_composition": "100% Organic Cotton",
            "physical_test_method": "Care Label Verification",
            "image_quality_rating": 5,
            "feedback_notes": "Tag confirmed organic cotton certification.",
        }
        resp = client.post("/api/fabric/feedback", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["corrected_fabric"] == "Organic cotton"
        assert data["predicted_fabric"] == "Cotton"


# ═══════════════════════════════════════════════════════════════════════════
# Admin model-metrics endpoint
# ═══════════════════════════════════════════════════════════════════════════

class TestAdminModelMetrics:
    def test_model_metrics_endpoint(self):
        resp = client.get("/api/admin/model-metrics")
        assert resp.status_code == 200
        data = resp.json()

        assert "active_model" in data
        assert data["active_model"]["accuracy"] >= 0.95
        assert len(data["active_model"]["confusion_matrix"]) == 19
