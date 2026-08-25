from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Project, ChatMessage, FabricAnalysis, ReferenceImage, User
from app.schemas.schemas import ChatMessageCreate, ChatMessageResponse
from app.api.v1.dependencies import get_current_user
from app.services.ai_chat import DesignAssistantService

router = APIRouter()
assistant_service = DesignAssistantService()

@router.get("/project/{project_id}", response_model=List[ChatMessageResponse])
def get_project_chat_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    messages = db.query(ChatMessage).filter(ChatMessage.project_id == project_id).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.post("/send", response_model=ChatMessageResponse)
def send_chat_message(
    msg_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == msg_in.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ref_image = db.query(ReferenceImage).filter(ReferenceImage.project_id == project.id).order_by(ReferenceImage.created_at.desc()).first()
    latest_analysis = None
    if ref_image:
        latest_analysis = db.query(FabricAnalysis).filter(FabricAnalysis.reference_image_id == ref_image.id).first()

    user_msg = ChatMessage(
        project_id=msg_in.project_id,
        user_id=current_user.id,
        sender="user",
        content=msg_in.content
    )
    db.add(user_msg)
    db.commit()

    ai_res = assistant_service.generate_response(msg_in.content, project, latest_analysis)

    assistant_msg = ChatMessage(
        project_id=msg_in.project_id,
        user_id=current_user.id,
        sender="assistant",
        content=ai_res["response_text"],
        metadata_json={"structured_concept": ai_res.get("structured_concept")} if ai_res.get("structured_concept") else {}
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg
