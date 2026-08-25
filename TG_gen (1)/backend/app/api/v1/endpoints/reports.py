from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Project, FabricAnalysis, Fabric, DyeMethod, User
from app.api.v1.dependencies import get_current_user
from app.services.impact_calculator import calculate_environmental_impact
from app.services.report_generator import generate_pdf_sustainability_report

router = APIRouter()

@router.get("/download")
def download_sustainability_report(
    analysis_id: int = Query(...),
    fabric_id: int = Query(...),
    dye_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(FabricAnalysis).filter(FabricAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Fabric analysis not found")

    project = db.query(Project).filter(Project.id == analysis.reference_image.project_id).first()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project report")

    selected_fabric = db.query(Fabric).filter(Fabric.id == fabric_id).first()
    if not selected_fabric:
        raise HTTPException(status_code=404, detail="Selected fabric not found")

    selected_dye = db.query(DyeMethod).filter(DyeMethod.id == dye_id).first()
    if not selected_dye:
        raise HTTPException(status_code=404, detail="Selected dye method not found")

    impact_data = calculate_environmental_impact(
        conventional_fabric_name="Conventional Cotton",
        selected_fabric=selected_fabric,
        conventional_dye_name="Conventional Synthetic Reactive Dye",
        selected_dye=selected_dye,
        garment_weight_kg=0.5
    )

    pdf_bytes = generate_pdf_sustainability_report(
        project=project,
        analysis=analysis,
        selected_fabric=selected_fabric,
        selected_dye=selected_dye,
        impact_data=impact_data
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=sustainability_report_project_{project.id}.pdf"}
    )
