from typing import Dict, Any
from app.models.models import Fabric, DyeMethod

FABRIC_BENCHMARKS = {
    "conventional cotton": {"water_per_kg": 9500.0, "co2_per_kg": 14.5, "chemical_idx": 85.0, "waste_kg": 0.4},
    "conventional polyester": {"water_per_kg": 1500.0, "co2_per_kg": 19.8, "chemical_idx": 90.0, "waste_kg": 0.5},
    "conventional wool": {"water_per_kg": 6500.0, "co2_per_kg": 24.0, "chemical_idx": 70.0, "waste_kg": 0.3},
    "organic cotton": {"water_per_kg": 2100.0, "co2_per_kg": 7.2, "chemical_idx": 15.0, "waste_kg": 0.15},
    "recycled cotton": {"water_per_kg": 400.0, "co2_per_kg": 3.8, "chemical_idx": 10.0, "waste_kg": 0.05},
    "hemp": {"water_per_kg": 2500.0, "co2_per_kg": 4.5, "chemical_idx": 12.0, "waste_kg": 0.1},
    "linen": {"water_per_kg": 2900.0, "co2_per_kg": 5.1, "chemical_idx": 18.0, "waste_kg": 0.12},
    "tencel/lyocell": {"water_per_kg": 1200.0, "co2_per_kg": 6.0, "chemical_idx": 20.0, "waste_kg": 0.1},
    "bamboo lyocell": {"water_per_kg": 1800.0, "co2_per_kg": 6.8, "chemical_idx": 22.0, "waste_kg": 0.12},
    "econyl/recycled nylon": {"water_per_kg": 800.0, "co2_per_kg": 8.5, "chemical_idx": 25.0, "waste_kg": 0.08},
    "deadstock fabric": {"water_per_kg": 0.0, "co2_per_kg": 0.5, "chemical_idx": 0.0, "waste_kg": 0.0},
    "peace silk": {"water_per_kg": 3200.0, "co2_per_kg": 9.0, "chemical_idx": 30.0, "waste_kg": 0.18},
    "organic wool": {"water_per_kg": 3500.0, "co2_per_kg": 12.0, "chemical_idx": 25.0, "waste_kg": 0.2}
}

DYE_WATER_FACTOR = {
    "very low": 0.1,
    "low": 0.3,
    "moderate": 0.6,
    "high": 1.0
}

def calculate_environmental_impact(
    conventional_fabric_name: str,
    selected_fabric: Fabric,
    conventional_dye_name: str,
    selected_dye: DyeMethod,
    garment_weight_kg: float = 0.5
) -> Dict[str, Any]:
    conv_key = conventional_fabric_name.lower()
    conv_bench = FABRIC_BENCHMARKS.get(conv_key, FABRIC_BENCHMARKS["conventional cotton"])

    sel_key = selected_fabric.name.lower()
    sel_bench = FABRIC_BENCHMARKS.get(sel_key, {
        "water_per_kg": (100 - selected_fabric.water_impact_score) * 65.0,
        "co2_per_kg": (100 - selected_fabric.carbon_impact_score) * 0.2,
        "chemical_idx": 20.0,
        "waste_kg": 0.15
    })

    conv_dye_water_mult = 1.0
    sel_dye_water_mult = DYE_WATER_FACTOR.get(selected_dye.water_impact_level.lower(), 0.3)

    conv_water_total = conv_bench["water_per_kg"] * garment_weight_kg * conv_dye_water_mult
    sel_water_total = sel_bench["water_per_kg"] * garment_weight_kg * sel_dye_water_mult

    conv_co2_total = conv_bench["co2_per_kg"] * garment_weight_kg
    sel_co2_total = sel_bench["co2_per_kg"] * garment_weight_kg

    water_saved = max(0.0, round(conv_water_total - sel_water_total, 1))
    co2_reduced = max(0.0, round(conv_co2_total - sel_co2_total, 2))
    
    waste_conv = conv_bench["waste_kg"] * garment_weight_kg
    waste_sel = sel_bench["waste_kg"] * garment_weight_kg
    waste_reduced = max(0.0, round(waste_conv - waste_sel, 2))

    chem_conv = conv_bench["chemical_idx"]
    chem_sel = sel_bench["chemical_idx"]
    chem_reduction_pct = max(0.0, round(((chem_conv - chem_sel) / max(1.0, chem_conv)) * 100, 1))

    water_pct_saved = round(((conv_water_total - sel_water_total) / max(1.0, conv_water_total)) * 100, 1)

    summary = (
        f"Choosing {selected_fabric.name} with {selected_dye.name} may reduce estimated water use by "
        f"{max(0, water_pct_saved)}% ({water_saved} L per garment) and avoid {co2_reduced} kg CO2 emissions "
        f"compared with {conventional_fabric_name}."
    )

    assumptions = [
        f"Standard garment baseline weight assumed at {garment_weight_kg} kg.",
        f"Conventional baseline: {conventional_fabric_name} with synthetic reactive dyeing.",
        "Figures represent average lifecycle modeling estimates and are provided for comparative analysis, not certified lab figures.",
        "Water consumption incorporates raw fiber agricultural/processing water and dye baths."
    ]

    return {
        "conventional_fabric": conventional_fabric_name,
        "selected_fabric": selected_fabric.name,
        "conventional_dye": conventional_dye_name,
        "selected_dye": selected_dye.name,
        "water_saved_liters": water_saved,
        "co2_reduced_kg": co2_reduced,
        "waste_reduced_kg": waste_reduced,
        "chemical_reduction_pct": chem_reduction_pct,
        "summary_text": summary,
        "assumptions": assumptions,
        "water_comparison": {
            "conventional": round(conv_water_total, 1),
            "sustainable": round(sel_water_total, 1)
        },
        "co2_comparison": {
            "conventional": round(conv_co2_total, 2),
            "sustainable": round(sel_co2_total, 2)
        }
    }
