from typing import List, Dict, Any
from app.models.models import Fabric, DyeMethod, FabricAnalysis

def evaluate_dye_recommendations(
    analysis: FabricAnalysis,
    selected_fabric: Fabric,
    dye_methods: List[DyeMethod]
) -> List[Dict[str, Any]]:
    results = []

    for dye in dye_methods:
        if not dye.is_active:
            continue

        fab_name = selected_fabric.name.lower()
        suitable = [s.lower() for s in (dye.suitable_fabrics or [])]

        is_compatible = any(s in fab_name or fab_name in s for s in suitable) or "all natural" in suitable or len(suitable) == 0
        compat_str = "High Compatibility" if is_compatible else "Moderate Compatibility"

        acc_rating = dye.color_accuracy_rating
        acc_str = f"{acc_rating}/5 Accuracy ({'Excellent' if acc_rating >= 4 else 'Moderate Shade Variance'})"

        rationale = f"Recommended for {selected_fabric.name} with {dye.water_impact_level.lower()} water usage and {dye.energy_impact_level.lower()} energy demands."
        if dye.process_type.lower() == "botanical":
            rationale += " Ideal for achieving organic, muted earthy hues."
        elif dye.process_type.lower() == "digital":
            rationale += " Zero water waste during print application with high color sharpness."
        elif dye.process_type.lower() == "dope dyeing":
            rationale += " Pigment integrated prior to fiber extrusion, saving up to 90% water."

        results.append({
            "dye_method": dye,
            "compatibility": compat_str,
            "color_accuracy": acc_str,
            "water_impact": dye.water_impact_level,
            "energy_impact": dye.energy_impact_level,
            "estimated_cost": dye.cost_level,
            "recommendation_rationale": rationale
        })

    return results
