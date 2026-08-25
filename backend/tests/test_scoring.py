from app.models.models import Fabric, FabricAnalysis
from app.schemas.schemas import PriorityWeights
from app.services.recommendation_engine import calculate_fabric_recommendations

def test_recommendation_scoring_highest_water():
    analysis = FabricAnalysis(
        garment_category="T-Shirt",
        fabric_type="Conventional Cotton",
        weave="Plain Weave",
        thickness="Medium"
    )

    fabrics = [
        Fabric(id=1, name="Hemp", category="Natural Regenerative", water_impact_score=90, carbon_impact_score=95, cost_level="Medium", is_vegan=True, is_recyclable=True, is_active=True),
        Fabric(id=2, name="Recycled Cotton", category="Recycled Natural", water_impact_score=98, carbon_impact_score=90, cost_level="Low", is_vegan=True, is_recyclable=True, is_active=True),
        Fabric(id=3, name="Conventional Wool", category="Natural Animal", water_impact_score=30, carbon_impact_score=40, cost_level="High", is_vegan=False, is_recyclable=True, is_active=True)
    ]

    weights = PriorityWeights(low_water=1.0, low_carbon=0.0, lowest_cost=0.0, closest_appearance=0.0, recyclability=0.0, vegan=0.0, durability=0.0)

    recs = calculate_fabric_recommendations(analysis, fabrics, weights)
    assert len(recs) == 3
    assert recs[0]["fabric"].name == "Recycled Cotton"
    assert recs[0]["match_percentage"] > recs[2]["match_percentage"]

def test_recommendation_scoring_vegan_preference():
    analysis = FabricAnalysis(garment_category="Blazer", fabric_type="Wool", weave="Twill")
    fabrics = [
        Fabric(id=1, name="Organic Wool", category="Natural Animal", water_impact_score=60, carbon_impact_score=60, cost_level="High", is_vegan=False, is_recyclable=True, is_active=True),
        Fabric(id=2, name="Tencel/Lyocell", category="Cellulosic Regenerative", water_impact_score=88, carbon_impact_score=85, cost_level="High", is_vegan=True, is_recyclable=True, is_active=True)
    ]

    weights = PriorityWeights(vegan=1.0, low_water=0.0, low_carbon=0.0, lowest_cost=0.0, closest_appearance=0.0, recyclability=0.0, durability=0.0)
    recs = calculate_fabric_recommendations(analysis, fabrics, weights)
    assert recs[0]["fabric"].name == "Tencel/Lyocell"
