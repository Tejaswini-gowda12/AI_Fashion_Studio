from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Project, User
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.api.v1.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.updated_at.desc()).all()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = Project(
        user_id=current_user.id,
        title=project_in.title,
        description=project_in.description,
        target_garment_type=project_in.target_garment_type,
        intended_season=project_in.intended_season,
        target_audience=project_in.target_audience,
        budget_range=project_in.budget_range,
        sustainability_goal=project_in.sustainability_goal
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, val in project_in.dict(exclude_unset=True).items():
        setattr(project, field, val)

    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()

@router.post("/{project_id}/duplicate", response_model=ProjectResponse)
def duplicate_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_project = Project(
        user_id=current_user.id,
        title=f"{project.title} (Copy)",
        description=project.description,
        target_garment_type=project.target_garment_type,
        intended_season=project.intended_season,
        target_audience=project.target_audience,
        budget_range=project.budget_range,
        sustainability_goal=project.sustainability_goal
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project
