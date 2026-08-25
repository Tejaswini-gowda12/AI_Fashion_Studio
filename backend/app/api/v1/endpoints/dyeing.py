from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import FabricAnalysis, Fabric, DyeMethod, User
from app.schemas.schemas import DyeRecommendationResponse
from app.api.v1.dependencies import get_current_user
from app.services.dyeing_engine import evaluate_dye_recommendations

router = APIRouter()

@router.get("/", response_model=List[DyeRecommendationResponse])
def get_dye_recommendations(
    analysis_id: int = Query(...),
    fabric_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Fabric analysis record not found")

    fabric = db.query(Fabric).filter(Fabric.id == fabric_id).first()
    if not fabric:
        raise HTTPException(status_code=404, detail="Fabric not found")

    dye_methods = db.query(DyeMethod).filter(DyeMethod.is_active == True).all()
    results = evaluate_dye_recommendations(analysis, fabric, dye_methods)
    return results
