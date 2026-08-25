from app.models.models import Fabric, DyeMethod
from app.services.impact_calculator import calculate_environmental_impact

def test_environmental_impact_calculation():
    hemp = Fabric(id=1, name="Hemp", water_impact_score=90, carbon_impact_score=95)
    natural_dye = DyeMethod(id=1, name="Natural Botanical Dyes", water_impact_level="Low", energy_impact_level="Low")

    impact = calculate_environmental_impact(
        conventional_fabric_name="Conventional Cotton",
        selected_fabric=hemp,
        conventional_dye_name="Conventional Synthetic Reactive Dye",
        selected_dye=natural_dye,
        garment_weight_kg=0.5
    )

    assert impact["water_saved_liters"] > 0
    assert impact["co2_reduced_kg"] > 0
    assert impact["chemical_reduction_pct"] > 0
    assert "Hemp" in impact["summary_text"]
    assert len(impact["assumptions"]) >= 3
