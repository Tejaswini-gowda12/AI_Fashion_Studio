import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.config import settings
from app.models.models import Project, ReferenceImage, FabricAnalysis, User
from app.schemas.schemas import FabricAnalysisResponse, FabricAnalysisUpdate
from app.api.v1.dependencies import get_current_user
from app.services.ai_vision import get_vision_analyzer

router = APIRouter()

@router.post("/upload", response_model=FabricAnalysisResponse)
async def upload_and_analyze_image(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload JPG, PNG, or WebP.")

    file_name = f"{uuid.uuid4().hex}{ext}"
    project_upload_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
    os.makedirs(project_upload_dir, exist_ok=True)
    saved_file_path = os.path.join(project_upload_dir, file_name)

    with open(saved_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    relative_path = f"/static/uploads/{project_id}/{file_name}"

    ref_img = ReferenceImage(
        project_id=project_id,
        file_path=relative_path,
        original_filename=file.filename
    )
    db.add(ref_img)
    db.commit()
    db.refresh(ref_img)

    vision_service = get_vision_analyzer(
        provider=settings.AI_VISION_PROVIDER,
        api_key=settings.OPENAI_API_KEY or settings.GEMINI_API_KEY
    )
    analysis_data = vision_service.analyze_image(saved_file_path)

    analysis = FabricAnalysis(
        reference_image_id=ref_img.id,
        garment_category=analysis_data["garment_category"],
        fabric_type=analysis_data["fabric_type"],
        dominant_colors=analysis_data["dominant_colors"],
        secondary_colors=analysis_data["secondary_colors"],
        pattern_type=analysis_data["pattern_type"],
        weave=analysis_data["weave"],
        shine=analysis_data["shine"],
        thickness=analysis_data["thickness"],
        stretch=analysis_data["stretch"],
        drape=analysis_data["drape"],
        opacity=analysis_data["opacity"],
        confidence_score=analysis_data["confidence_score"],
        is_user_corrected=False
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis

@router.get("/{analysis_id}", response_model=FabricAnalysisResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.put("/{analysis_id}", response_model=FabricAnalysisResponse)
def update_analysis_attributes(
    analysis_id: int,
    update_in: FabricAnalysisUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    for field, val in update_in.dict(exclude_unset=True).items():
        setattr(analysis, field, val)

    analysis.is_user_corrected = True
    db.commit()
    db.refresh(analysis)
    return analysis
