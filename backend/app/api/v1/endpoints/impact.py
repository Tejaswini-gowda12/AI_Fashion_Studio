from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import FabricAnalysis, Fabric, DyeMethod, ImpactAssessment, User
from app.schemas.schemas import ImpactCalculateRequest, ImpactAssessmentResponse
from app.api.v1.dependencies import get_current_user
from app.services.impact_calculator import calculate_environmental_impact

router = APIRouter()

@router.post("/calculate", response_model=ImpactAssessmentResponse)
def compute_impact(
    req: ImpactCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == req.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Fabric analysis record not found")

    selected_fabric = db.query(Fabric).filter(Fabric.id == req.selected_fabric_id).first()
    if not selected_fabric:
        raise HTTPException(status_code=404, detail="Selected fabric not found")

    selected_dye = db.query(DyeMethod).filter(DyeMethod.id == req.selected_dye_id).first()
    if not selected_dye:
        raise HTTPException(status_code=404, detail="Selected dye method not found")

    impact_res = calculate_environmental_impact(
        conventional_fabric_name=req.conventional_fabric_name or "Conventional Cotton",
        selected_fabric=selected_fabric,
        conventional_dye_name=req.conventional_dye_name or "Conventional Synthetic Reactive Dye",
        selected_dye=selected_dye,
        garment_weight_kg=req.garment_weight_kg or 0.5
    )

    assessment = ImpactAssessment(
        analysis_id=req.analysis_id,
        selected_fabric_id=req.selected_fabric_id,
        selected_dye_id=req.selected_dye_id,
        water_saved_liters=impact_res["water_saved_liters"],
        co2_reduced_kg=impact_res["co2_reduced_kg"],
        waste_reduced_kg=impact_res["waste_reduced_kg"],
        chemical_reduction_pct=impact_res["chemical_reduction_pct"],
        summary_text=impact_res["summary_text"],
        assumptions_json={"assumptions": impact_res["assumptions"]}
    )
    db.add(assessment)
    db.commit()

    return {
        "analysis_id": req.analysis_id,
        "conventional_fabric": impact_res["conventional_fabric"],
        "selected_fabric": impact_res["selected_fabric"],
        "conventional_dye": impact_res["conventional_dye"],
        "selected_dye": impact_res["selected_dye"],
        "water_saved_liters": impact_res["water_saved_liters"],
        "co2_reduced_kg": impact_res["co2_reduced_kg"],
        "waste_reduced_kg": impact_res["waste_reduced_kg"],
        "chemical_reduction_pct": impact_res["chemical_reduction_pct"],
        "summary_text": impact_res["summary_text"],
        "assumptions": impact_res["assumptions"],
        "water_comparison": impact_res["water_comparison"],
        "co2_comparison": impact_res["co2_comparison"]
    }
