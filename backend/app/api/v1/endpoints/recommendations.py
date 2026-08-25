from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import FabricAnalysis, Fabric, User
from app.schemas.schemas import RecommendationQuery, FabricRecommendationResponse
from app.api.v1.dependencies import get_current_user
from app.services.recommendation_engine import calculate_fabric_recommendations

router = APIRouter()

@router.post("/", response_model=List[FabricRecommendationResponse])
def get_recommendations(
    query: RecommendationQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == query.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Fabric analysis record not found")

    fabrics = db.query(Fabric).filter(Fabric.is_active == True).all()
    recommendations = calculate_fabric_recommendations(analysis, fabrics, query.weights)
    return recommendations
