from typing import List, Dict, Any
from app.models.models import Fabric, FabricAnalysis
from app.schemas.schemas import PriorityWeights

def calculate_fabric_recommendations(
    analysis: FabricAnalysis,
    fabrics: List[Fabric],
    weights: PriorityWeights
) -> List[Dict[str, Any]]:
    results = []
    cost_map = {"Low": 1.0, "Medium": 0.75, "High": 0.5, "Premium": 0.3}

    for fab in fabrics:
        if not fab.is_active:
            continue

        water_score = fab.water_impact_score or 70
        carbon_score = fab.carbon_impact_score or 70
        recyclability_score = 100 if fab.is_recyclable else 30
        vegan_score = 100 if fab.is_vegan else 0
        durability_rating = fab.durability_rating if fab.durability_rating is not None else 4
        durability_score = durability_rating * 20
        cost_score = cost_map.get(fab.cost_level or "Medium", 0.5) * 100

        similarity_score = 70.0
        reasons = []

        analysis_weave_lower = (analysis.weave or "").lower()
        if any(tag in analysis_weave_lower for tag in (fab.texture_tags or [])):
            similarity_score += 15
            reasons.append(f"Matches observed texture ({analysis.weave})")

        fab_cat_lower = (fab.category or "").lower()
        if fab_cat_lower in ("natural", "regenerative") or "natural" in fab_cat_lower:
            similarity_score += 10
            reasons.append(f"High aesthetic compatibility with {analysis.garment_category}")

        similarity_score = min(100.0, similarity_score)

        w_cost = weights.lowest_cost
        w_app = weights.closest_appearance
        w_water = weights.low_water
        w_carbon = weights.low_carbon
        w_recycle = weights.recyclability
        w_vegan = weights.vegan
        w_durable = weights.durability

        total_weight = w_cost + w_app + w_water + w_carbon + w_recycle + w_vegan + w_durable
        if total_weight == 0:
            total_weight = 1.0

        weighted_sum = (
            (cost_score * w_cost) +
            (similarity_score * w_app) +
            (water_score * w_water) +
            (carbon_score * w_carbon) +
            (recyclability_score * w_recycle) +
            (vegan_score * w_vegan) +
            (durability_score * w_durable)
        )

        final_match_pct = round(weighted_sum / total_weight, 1)

        if fab.water_impact_score and fab.water_impact_score >= 85:
            reasons.append("Ultra-low water consumption footprint")
        if fab.carbon_impact_score and fab.carbon_impact_score >= 85:
            reasons.append("Low carbon emissions profile")
        if fab.is_recyclable:
            reasons.append("Fully recyclable at end-of-life")
        if fab.is_vegan and weights.vegan > 0.5:
            reasons.append("100% Cruelty-free & Vegan certified")
        if fab.cost_level in ("Low", "Medium") and weights.lowest_cost > 0.5:
            reasons.append("Economical cost structure for target budget")

        breakdown = {
            "eco_score": round((water_score + carbon_score) / 2, 1),
            "appearance_similarity": round(similarity_score, 1),
            "water_impact_score": water_score,
            "carbon_impact_score": carbon_score,
            "cost_level": fab.cost_level,
            "durability_rating": fab.durability_rating,
            "applied_weights": weights.dict()
        }

        results.append({
            "fabric": fab,
            "match_percentage": final_match_pct,
            "calculation_breakdown": breakdown,
            "match_reasons": reasons[:4]
        })

    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results[:5]
