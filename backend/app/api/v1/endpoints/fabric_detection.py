import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.models.models import FabricAnalysis, UploadedImage, PredictionFeedback, User
from app.schemas.schemas import (
    FabricDetectionRecordResponse, FabricAnalysisCorrection, FabricAnalyzeResponse,
    PredictionFeedbackCreate, PredictionFeedbackResponse, TopPredictionItem,
    VisibleFeatures, ImageQualityMetrics
)
from app.services.color_texture_processor import validate_image
from app.services.image_quality_analyzer import analyze_image_quality
from app.services.fabric_detection_service import get_fabric_detection_service, get_fabric_details
from app.api.v1.dependencies import get_current_user_optional

router = APIRouter()


@router.post("/analyze", response_model=FabricAnalyzeResponse)
async def analyze_fabric_image(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    POST /api/fabric/analyze
    1. Uploads JPG, JPEG, PNG, or WebP image up to 10 MB.
    2. Validates image resolution (min 512×512), blur, exposure, and fabric coverage —
       returning per-check pass/fail with exact failure messages.
    3. Runs AI & Computer Vision inference.
    4. If confidence < 0.75 or resolution fails, flags prediction_status as 'uncertain'.
    5. Returns structured JSON including explanation, visible_features, and image_quality.
    """
    file_bytes = await file.read()

    # ── 1. Format & Size Validation ─────────────────────────────────────────
    is_valid_format, err_msg = validate_image(file_bytes, file.filename, max_mb=settings.MAX_UPLOAD_SIZE_MB)
    if not is_valid_format:
        raise HTTPException(status_code=400, detail=err_msg)

    # ── 2. Image-Quality Validation (structured per-check result) ────────────
    quality_res = analyze_image_quality(file_bytes, file.filename)

    # ── 3. Save uploaded file ─────────────────────────────────────────────────
    ext       = os.path.splitext(file.filename)[1].lower()
    # Preserve the original stem in the saved filename for detection-service triggers
    # (e.g. 'lowconf' or 'blurry' in filename triggers low-confidence mock path)
    orig_stem = os.path.splitext(os.path.basename(file.filename))[0][:32]  # max 32 chars
    file_name = f"{uuid.uuid4().hex}_{orig_stem}{ext}"
    upload_dir     = os.path.join(settings.UPLOAD_DIR, "fabric_detection")
    os.makedirs(upload_dir, exist_ok=True)
    saved_file_path = os.path.join(upload_dir, file_name)

    with open(saved_file_path, "wb") as f:
        f.write(file_bytes)

    image_url = f"/static/uploads/fabric-detection/{file_name}"

    # ── 4. Record uploaded image metadata ────────────────────────────────────
    # UploadedImage.quality_score is a Float column (0-1 range)
    # UploadedImage.lighting_status is a String column
    # UploadedImage.fabric_coverage is a Float column (0-1 range)
    # UploadedImage.quality_warning is a Text column
    checks = quality_res.get("checks", {})
    coverage_check = checks.get("fabric_coverage", {})
    coverage_actual_str = coverage_check.get("actual", "85%").replace("%", "")
    try:
        coverage_float = float(coverage_actual_str) / 100.0
    except (ValueError, TypeError):
        coverage_float = quality_res.get("fabric_coverage", 0.85)

    uploaded_img_record = UploadedImage(
        file_path=saved_file_path,
        original_filename=file.filename,
        file_size_bytes=len(file_bytes),
        mime_type=file.content_type or f"image/{ext.replace('.', '')}",
        width=quality_res["width"],
        height=quality_res["height"],
        blur_score=quality_res.get("laplacian_var", 100.0),
        lighting_status=quality_res.get("lighting", "good"),
        fabric_coverage=coverage_float,
        quality_score=quality_res.get("score", 0.89),        # Float 0-1 column
        is_valid_quality=quality_res["is_valid"],
        quality_warning=quality_res.get("warning"),
    )
    db.add(uploaded_img_record)
    db.commit()

    # ── 5. AI & Computer Vision Prediction ───────────────────────────────────
    detection_service = get_fabric_detection_service()
    result = detection_service.analyze(saved_file_path)

    # Build top-3 predictions — prefer new top_predictions from service, fallback to alts
    if result.top_predictions:
        top_predictions_items = result.top_predictions[:3]
    else:
        top_predictions_items = [
            TopPredictionItem(fabric=result.detected_fabric, confidence=result.confidence_score)
        ]
        for alt in result.alternative_possible_fabrics[:2]:
            top_predictions_items.append(TopPredictionItem(fabric=alt.name, confidence=alt.confidence))

    # ── 6. Prediction status (0.75 confidence threshold + resolution check) ──
    res_check_passed = checks.get("resolution", {}).get("passed", quality_res.get("min_resolution_passed", True))
    if result.confidence_score >= 0.75 and res_check_passed:
        prediction_status = "high_confidence"
    else:
        prediction_status = "uncertain"

    # ── 7. Limitation disclaimer ─────────────────────────────────────────────
    limitations_text = (
        "This is an AI visual estimate. Exact fiber composition and sustainability "
        "attributes require label verification or laboratory testing."
    )
    recommended_next_step = (
        "Check the garment label or conduct a physical composition test "
        "if exact material confirmation is required."
    )

    dominant_colors_json  = [c.dict() for c in result.dominant_colors]
    alternatives_json     = [a.dict() for a in result.alternative_possible_fabrics]
    material_props_json   = result.material_properties.dict()

    user_id = current_user.id if current_user else None

    # ── 8. Save Analysis to DB ───────────────────────────────────────────────
    analysis = FabricAnalysis(
        user_id=user_id,
        image_url=image_url,
        garment_type=result.garment_type,
        garment_category=result.garment_type,
        detected_fabric=result.detected_fabric,
        fabric_type=result.detected_fabric,
        confidence_score=result.confidence_score,
        alternative_possible_fabrics=alternatives_json,
        texture=result.texture,
        weave_or_knit_type=result.weave_or_knit_type,
        pattern=result.pattern,
        dominant_colors=dominant_colors_json,
        secondary_colors=dominant_colors_json[1:] if len(dominant_colors_json) > 1 else [],
        material_properties=material_props_json,
        sustainability_note=limitations_text,
        is_user_corrected=False,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # ── 9. Build response objects ─────────────────────────────────────────────
    visible_features = VisibleFeatures(
        texture=result.texture,
        weave=result.weave_or_knit_type,
        pattern=result.pattern,
        thickness=material_props_json.get("thickness", "medium"),
        shine=material_props_json.get("shine", "matte"),
        stretch=material_props_json.get("stretch", "low"),
        opacity=material_props_json.get("opacity", "opaque"),
    )

    # Build full ImageQualityMetrics with both structured and flat fields
    image_quality_dict = {
        "is_valid":               quality_res["is_valid"],
        "quality_score":          quality_res["quality_score"],
        "checks":                 quality_res.get("checks"),
        "user_guidance":          quality_res.get("user_guidance", []),
        # backward-compat flat aliases
        "score":                  quality_res.get("score", 0.89),
        "blur":                   quality_res.get("blur", "low"),
        "lighting":               quality_res.get("lighting", "good"),
        "fabric_coverage":        quality_res.get("fabric_coverage", 0.85),
        "min_resolution_passed":  quality_res.get("min_resolution_passed", True),
        "warning":                quality_res.get("warning"),
    }

    details = get_fabric_details(result.detected_fabric)

    # Retrieve explanation from service result
    explanation = result.explanation or (
        f"Visual analysis detected {result.detected_fabric} based on optical surface texture, "
        f"weave geometry, and color distribution patterns."
    )

    return FabricAnalyzeResponse(
        id=analysis.id,
        predicted_fabric=result.detected_fabric,
        detected_fabric=result.detected_fabric,
        confidence=result.confidence_score,
        confidence_score=result.confidence_score,
        status=prediction_status,
        prediction_status=prediction_status,
        top_predictions=top_predictions_items,
        explanation=explanation,
        visible_features=visible_features,
        image_quality=image_quality_dict,
        limitations=limitations_text,
        recommended_next_step=recommended_next_step,
        fabric_details=details,
        user_corrected_fabric=None,
        is_user_corrected=False,
        dominant_colors=dominant_colors_json,
        material_properties=material_props_json,
        image_url=image_url,
        created_at=analysis.created_at,
    )


@router.get("/analyses", response_model=List[FabricDetectionRecordResponse])
@router.get("/history", response_model=List[FabricDetectionRecordResponse])
def get_fabric_analyses_history(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    GET /api/fabric/analyses or /api/fabric-detection/history
    """
    query = db.query(FabricAnalysis)
    if current_user:
        query = query.filter(FabricAnalysis.user_id == current_user.id)

    records = query.order_by(FabricAnalysis.created_at.desc()).all()
    return records


@router.get("/analyses/{analysis_id}", response_model=FabricDetectionRecordResponse)
@router.get("/{analysis_id}", response_model=FabricDetectionRecordResponse)
def get_fabric_analysis_by_id(analysis_id: int, db: Session = Depends(get_db)):
    """
    GET /api/fabric/analyses/{id}
    """
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Fabric analysis not found")
    return analysis


@router.patch("/analyses/{analysis_id}/correction", response_model=FabricDetectionRecordResponse)
@router.patch("/{analysis_id}", response_model=FabricDetectionRecordResponse)
def update_fabric_analysis_correction(
    analysis_id: int,
    payload: FabricAnalysisCorrection,
    db: Session = Depends(get_db)
):
    """
    PATCH /api/fabric/analyses/{id}/correction
    Saves user manual fabric type correction.
    """
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Fabric analysis not found")

    analysis.user_corrected_fabric = payload.user_corrected_fabric
    analysis.is_user_corrected = True

    if payload.garment_type:
        analysis.garment_type = payload.garment_type
        analysis.garment_category = payload.garment_type

    if payload.material_properties:
        analysis.material_properties = payload.material_properties.dict()

    db.commit()
    db.refresh(analysis)
    return analysis


@router.post("/feedback", response_model=PredictionFeedbackResponse)
def create_prediction_feedback(
    payload: PredictionFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    POST /api/fabric/feedback
    Saves verified composition feedback for ML model fine-tuning.
    """
    user_id = current_user.id if current_user else None

    feedback = PredictionFeedback(
        analysis_id=payload.analysis_id,
        user_id=user_id,
        predicted_fabric=payload.predicted_fabric,
        corrected_fabric=payload.corrected_fabric,
        verified_composition=payload.verified_composition,
        physical_test_method=payload.physical_test_method,
        image_quality_rating=payload.image_quality_rating or 5,
        feedback_notes=payload.feedback_notes,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.delete("/{analysis_id}")
@router.delete("/analyses/{analysis_id}")
def delete_fabric_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Deletes fabric analysis record.
    """
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Fabric analysis not found")

    db.delete(analysis)
    db.commit()
    return {"message": "Fabric analysis deleted successfully", "id": analysis_id}
