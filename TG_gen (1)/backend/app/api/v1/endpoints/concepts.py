from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Project, DesignConcept, User
from app.schemas.schemas import DesignConceptCreate, DesignConceptResponse
from app.api.v1.dependencies import get_current_user

router = APIRouter()

@router.get("/project/{project_id}", response_model=List[DesignConceptResponse])
def get_project_concepts(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(DesignConcept).filter(DesignConcept.project_id == project_id).order_by(DesignConcept.created_at.desc()).all()

@router.post("/", response_model=DesignConceptResponse, status_code=status.HTTP_201_CREATED)
def create_concept(
    concept_in: DesignConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == concept_in.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    concept = DesignConcept(
        project_id=concept_in.project_id,
        design_name=concept_in.design_name,
        inspiration_summary=concept_in.inspiration_summary,
        silhouette=concept_in.silhouette,
        material_recommendation=concept_in.material_recommendation,
        color_palette=concept_in.color_palette or [],
        dyeing_method=concept_in.dyeing_method,
        trims=concept_in.trims,
        sustainability_rationale=concept_in.sustainability_rationale,
        production_notes=concept_in.production_notes
    )
    db.add(concept)
    db.commit()
    db.refresh(concept)
    return concept
