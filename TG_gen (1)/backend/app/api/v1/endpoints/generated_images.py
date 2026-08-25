from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Project, DesignConcept, ReferenceImage, FabricAnalysis, GeneratedImage, User
from app.schemas.schemas import GeneratedImageRequest, GeneratedImageResponse
from app.api.v1.dependencies import get_current_user
from app.services.ai_image import ConceptImageGenerator

router = APIRouter()
image_generator = ConceptImageGenerator()

@router.get("/project/{project_id}", response_model=List[GeneratedImageResponse])
def get_project_generated_images(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(GeneratedImage).filter(GeneratedImage.project_id == project_id).order_by(GeneratedImage.created_at.desc()).all()

@router.post("/generate", response_model=GeneratedImageResponse, status_code=status.HTTP_201_CREATED)
def generate_concept_image(
    req: GeneratedImageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    concept = None
    if req.concept_id:
        concept = db.query(DesignConcept).filter(DesignConcept.id == req.concept_id).first()

    ref_image = db.query(ReferenceImage).filter(ReferenceImage.project_id == project.id).order_by(ReferenceImage.created_at.desc()).first()
    analysis = None
    if ref_image:
        analysis = db.query(FabricAnalysis).filter(FabricAnalysis.reference_image_id == ref_image.id).first()

    res = image_generator.generate_concept_image(
        project=project,
        concept=concept,
        analysis=analysis,
        custom_prompt_suffix=req.custom_prompt_suffix or ""
    )

    gen_img = GeneratedImage(
        project_id=req.project_id,
        concept_id=req.concept_id,
        prompt=res["prompt"],
        image_url=res["image_url"],
        generation_mode=res["generation_mode"]
    )
    db.add(gen_img)
    db.commit()
    db.refresh(gen_img)
    return gen_img
