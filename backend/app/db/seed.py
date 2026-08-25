from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.models import User, Fabric, DyeMethod, Project, ReferenceImage, FabricAnalysis, DesignConcept, ChatMessage
from app.core.security import get_password_hash

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        admin_user = db.query(User).filter(User.email == "admin@eco.fashion").first()
        if not admin_user:
            admin_user = User(
                email="admin@eco.fashion",
                hashed_password=get_password_hash("admin123"),
                full_name="Eco Fashion Admin",
                role="admin",
                sustainability_preferences={"low_water": 90, "low_carbon": 90, "vegan": True},
                preferred_materials=["Hemp", "Organic Cotton", "Tencel/Lyocell"]
            )
            db.add(admin_user)

        demo_user = db.query(User).filter(User.email == "designer@eco.fashion").first()
        if not demo_user:
            demo_user = User(
                email="designer@eco.fashion",
                hashed_password=get_password_hash("designer123"),
                full_name="Aria Vance (Senior Designer)",
                role="user",
                sustainability_preferences={"lowest_cost": 40, "closest_appearance": 85, "low_water": 95, "low_carbon": 90},
                preferred_materials=["Organic Cotton", "Hemp", "Recycled Polyester", "Econyl/recycled nylon"]
            )
            db.add(demo_user)

        db.commit()
        db.refresh(admin_user)
        db.refresh(demo_user)

        seed_fabrics = [
            {
                "name": "Organic Cotton",
                "category": "Natural Plant",
                "fiber_source": "Non-GMO Cotton Plant",
                "water_impact_score": 75,
                "carbon_impact_score": 70,
                "biodegradability_score": 95,
                "cost_level": "Medium",
                "durability_rating": 4,
                "comfort_rating": 5,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["soft", "breathable", "plain weave", "twill"],
                "pros": ["Zero toxic synthetic pesticides", "High skin comfort & breathability", "Fully biodegradable"],
                "limitations": ["Requires higher agricultural land than hemp", "Higher water use than recycled fibers"],
                "best_use_cases": ["T-Shirts", "Casual Shirts", "Underwear", "Light Jackets"]
            },
            {
                "name": "Recycled Cotton",
                "category": "Recycled Natural",
                "fiber_source": "Post-Industrial / Post-Consumer Scrap",
                "water_impact_score": 95,
                "carbon_impact_score": 90,
                "biodegradability_score": 90,
                "cost_level": "Low",
                "durability_rating": 3,
                "comfort_rating": 4,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["soft", "heathered", "knit", "plain weave"],
                "pros": ["Near zero agricultural water footprint", "Diverts textile waste from landfill"],
                "limitations": ["Shorter staple fiber length requires blending for strength"],
                "best_use_cases": ["Sweatshirts", "Denim Blends", "Tote Bags"]
            },
            {
                "name": "Hemp",
                "category": "Natural Regenerative",
                "fiber_source": "Cannabis Sativa Bast Fiber",
                "water_impact_score": 90,
                "carbon_impact_score": 95,
                "biodegradability_score": 100,
                "cost_level": "Medium",
                "durability_rating": 5,
                "comfort_rating": 4,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["structured", "twill", "textured", "heavy canvas"],
                "pros": ["Sequesters 4x more CO2 than trees", "3x stronger than cotton", "Pest resistant natural growth"],
                "limitations": ["Requires softening wash cycles initially"],
                "best_use_cases": ["Denim Jackets", "Workwear Trousers", "Structured Outerwear"]
            },
            {
                "name": "Linen",
                "category": "Natural Plant",
                "fiber_source": "Flax Plant Bast Fiber",
                "water_impact_score": 85,
                "carbon_impact_score": 88,
                "biodegradability_score": 100,
                "cost_level": "High",
                "durability_rating": 4,
                "comfort_rating": 4,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["textured", "slub", "breathable", "plain weave"],
                "pros": ["Naturally moisture-wicking and thermo-regulating", "Grows in poor soil without irrigation"],
                "limitations": ["Wrinkles easily, higher price point"],
                "best_use_cases": ["Summer Shirts", "Dresses", "Relaxed Tailoring"]
            },
            {
                "name": "Tencel/Lyocell",
                "category": "Cellulosic Regenerative",
                "fiber_source": "Sustainably Harvested Wood Pulp",
                "water_impact_score": 88,
                "carbon_impact_score": 85,
                "biodegradability_score": 95,
                "cost_level": "High",
                "durability_rating": 4,
                "comfort_rating": 5,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["smooth", "silky", "fluid drape", "satin sheen"],
                "pros": ["Closed-loop solvent recycling (99.5% recovery)", "Silky smooth drape & luster"],
                "limitations": ["Requires chemical solvent processing (though non-toxic)"],
                "best_use_cases": ["Evening Dresses", "Silky Blouses", "Activewear Lining"]
            },
            {
                "name": "Bamboo Lyocell",
                "category": "Cellulosic Regenerative",
                "fiber_source": "Organic Bamboo Stems",
                "water_impact_score": 85,
                "carbon_impact_score": 82,
                "biodegradability_score": 95,
                "cost_level": "Medium",
                "durability_rating": 4,
                "comfort_rating": 5,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["soft", "breathable", "fluid drape", "knit"],
                "pros": ["Rapidly renewable crop (grows up to 1 meter/day)", "Antibacterial natural properties"],
                "limitations": ["Must use closed-loop lyocell process to avoid harsh viscose chemicals"],
                "best_use_cases": ["Loungewear", "Base Layers", "Undergarments"]
            },
            {
                "name": "Recycled Polyester",
                "category": "Recycled Synthetic",
                "fiber_source": "Post-Consumer PET Bottles",
                "water_impact_score": 92,
                "carbon_impact_score": 75,
                "biodegradability_score": 10,
                "cost_level": "Low",
                "durability_rating": 5,
                "comfort_rating": 3,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["smooth", "synthetic", "quick-dry", "matte"],
                "pros": ["Prevents plastic pollution in ocean/landfills", "Requires 59% less energy than virgin rPET"],
                "limitations": ["Sheds microplastics during wash (requires guppy bag/filter)", "Non-biodegradable"],
                "best_use_cases": ["Activewear Shells", "Performance Jackets", "Fleece Lining"]
            },
            {
                "name": "Econyl/recycled nylon",
                "category": "Recycled Synthetic",
                "fiber_source": "Ocean Fishing Nets & Industrial Nylon Scrap",
                "water_impact_score": 90,
                "carbon_impact_score": 80,
                "biodegradability_score": 10,
                "cost_level": "High",
                "durability_rating": 5,
                "comfort_rating": 4,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["stretch", "smooth", "high resilience", "matte"],
                "pros": ["Cleans ocean waste", "Infinitely recyclable without quality loss"],
                "limitations": ["Requires micro-filter washing bag"],
                "best_use_cases": ["Swimwear", "Compressive Activewear", "Technical Outerwear"]
            },
            {
                "name": "Deadstock Fabric",
                "category": "Upcycled / Circular",
                "fiber_source": "Surplus Factory Over-production Scrap",
                "water_impact_score": 100,
                "carbon_impact_score": 98,
                "biodegradability_score": 70,
                "cost_level": "Low",
                "durability_rating": 4,
                "comfort_rating": 4,
                "is_vegan": True,
                "is_recyclable": True,
                "texture_tags": ["varied", "textured", "twill", "plain weave"],
                "pros": ["Zero additional resource extraction", "Unique limited-edition production potential"],
                "limitations": ["Irregular yardage availability", "Inconsistent fiber verification"],
                "best_use_cases": ["Capsule Collections", "Patchwork Outerwear", "Limited Edition Run"]
            },
            {
                "name": "Peace Silk",
                "category": "Natural Animal-Friendly",
                "fiber_source": "Ahimsa Mulberry Silkworm Cocoons",
                "water_impact_score": 65,
                "carbon_impact_score": 70,
                "biodegradability_score": 100,
                "cost_level": "Premium",
                "durability_rating": 4,
                "comfort_rating": 5,
                "is_vegan": False,
                "is_recyclable": True,
                "texture_tags": ["silky", "satin sheen", "fluid drape", "luxurious"],
                "pros": ["Moth emerges naturally without boiling pupae", "Luxurious natural hand-feel"],
                "limitations": ["Non-vegan", "Higher cost per yard"],
                "best_use_cases": ["Couture Gowns", "Luxury Scarves", "Formal Wear"]
            },
            {
                "name": "Organic Wool",
                "category": "Natural Animal",
                "fiber_source": "Certified Organic Sheep Fleece",
                "water_impact_score": 60,
                "carbon_impact_score": 55,
                "biodegradability_score": 95,
                "cost_level": "Premium",
                "durability_rating": 5,
                "comfort_rating": 4,
                "is_vegan": False,
                "is_recyclable": True,
                "texture_tags": ["warm", "textured knit", "heavyweight", "matte"],
                "pros": ["High thermal efficiency", "Ethical pasture management & cruelty-free shearing"],
                "limitations": ["Methane agricultural emissions from livestock"],
                "best_use_cases": ["Winter Overcoats", "Heavy Tailored Suits", "Thick Knits"]
            }
        ]

        for fab_data in seed_fabrics:
            existing_fab = db.query(Fabric).filter(Fabric.name == fab_data["name"]).first()
            if not existing_fab:
                db.add(Fabric(**fab_data))

        seed_dyes = [
            {
                "name": "Natural Botanical Dyes",
                "process_type": "Botanical Plant",
                "water_impact_level": "Low",
                "energy_impact_level": "Low",
                "cost_level": "Medium",
                "color_accuracy_rating": 4,
                "limitation_notes": "Organic shade variance between batches; requires natural alum mordant for lightfastness.",
                "suitable_fabrics": ["Organic Cotton", "Hemp", "Linen", "Peace Silk", "Bamboo Lyocell"]
            },
            {
                "name": "Low-Impact Fiber-Reactive Dyes",
                "process_type": "Low-Toxicity Chemical",
                "water_impact_level": "Moderate",
                "energy_impact_level": "Low",
                "cost_level": "Low",
                "color_accuracy_rating": 5,
                "limitation_notes": "Requires high fixative rates; heavy metals & azo compounds strictly excluded.",
                "suitable_fabrics": ["Organic Cotton", "Recycled Cotton", "Linen", "Tencel/Lyocell"]
            },
            {
                "name": "Digital Textile Printing",
                "process_type": "Digital Inkjet",
                "water_impact_level": "Very Low",
                "energy_impact_level": "Low",
                "cost_level": "Medium",
                "color_accuracy_rating": 5,
                "limitation_notes": "Best suited for pattern placement rather than solid piece dyeing.",
                "suitable_fabrics": ["Tencel/Lyocell", "Recycled Polyester", "Peace Silk", "Organic Cotton"]
            },
            {
                "name": "Dope Dyeing (Solution Dyeing)",
                "process_type": "Pre-Extrusion Masterbatch",
                "water_impact_level": "Very Low",
                "energy_impact_level": "Low",
                "cost_level": "Low",
                "color_accuracy_rating": 5,
                "limitation_notes": "Color pigment added during polymer melt; minimum batch sizes required.",
                "suitable_fabrics": ["Recycled Polyester", "Econyl/recycled nylon"]
            },
            {
                "name": "Waterless Supercritical CO2 Dyeing",
                "process_type": "Waterless Gas Extraction",
                "water_impact_level": "Very Low",
                "energy_impact_level": "Medium",
                "cost_level": "High",
                "color_accuracy_rating": 5,
                "limitation_notes": "Requires specialized high-pressure CO2 machinery.",
                "suitable_fabrics": ["Recycled Polyester", "Econyl/recycled nylon"]
            },
            {
                "name": "Undyed / Natural Color Fabric",
                "process_type": "Zero Chemical",
                "water_impact_level": "Very Low",
                "energy_impact_level": "Very Low",
                "cost_level": "Low",
                "color_accuracy_rating": 3,
                "limitation_notes": "Limited to raw natural fiber colors (ecru, off-white, natural brown/green cotton).",
                "suitable_fabrics": ["Organic Cotton", "Hemp", "Linen", "Organic Wool"]
            }
        ]

        for dye_data in seed_dyes:
            existing_dye = db.query(DyeMethod).filter(DyeMethod.name == dye_data["name"]).first()
            if not existing_dye:
                db.add(DyeMethod(**dye_data))

        db.commit()

        existing_proj = db.query(Project).filter(Project.title == "Autumn Eco Blazer Concept").first()
        if not existing_proj:
            proj = Project(
                user_id=demo_user.id,
                title="Autumn Eco Blazer Concept",
                description="Tailored structured blazer with low water consumption footprint and 100% biodegradable fiber goal.",
                target_garment_type="Structured Blazer",
                intended_season="Autumn/Winter",
                target_audience="Eco-Conscious Professional",
                budget_range="Medium",
                sustainability_goal="Reduce baseline water usage by 60% and use botanical non-toxic dyes."
            )
            db.add(proj)
            db.commit()
            db.refresh(proj)

            ref_img = ReferenceImage(
                project_id=proj.id,
                file_path="/static/uploads/demo/blazer_ref.jpg",
                original_filename="vintage_tweed_blazer.jpg"
            )
            db.add(ref_img)
            db.commit()
            db.refresh(ref_img)

            analysis = FabricAnalysis(
                reference_image_id=ref_img.id,
                garment_category="Structured Blazer",
                fabric_type="Conventional Wool-Polyester Blend Tweed",
                dominant_colors=["#2B3A42", "#8A9A86"],
                secondary_colors=["#C86D51"],
                pattern_type="Twill Weave",
                weave="Twill",
                shine="Matte",
                thickness="Heavyweight",
                stretch="None",
                drape="Stiff",
                opacity="Opaque",
                confidence_score=0.94,
                is_user_corrected=False
            )
            db.add(analysis)
            db.commit()

            concept = DesignConcept(
                project_id=proj.id,
                design_name="Hemp-Linen Tailored Blazer",
                inspiration_summary="Minimalist structured blazer retaining heritage tweed texture using organic bast fibers.",
                silhouette="Single-breasted relaxed tailored blazer",
                material_recommendation="100% Organic Hemp Heavy Twill",
                color_palette=["#2B3A42", "#8A9A86", "#C86D51"],
                dyeing_method="Natural Botanical Dye",
                trims="Natural Corozo nut buttons",
                sustainability_rationale="Cuts water footprint by 65%, 100% biodegradable bast fiber construction.",
                production_notes="Cut using zero-waste pattern layout."
            )
            db.add(concept)
            
            chat_msg = ChatMessage(
                project_id=proj.id,
                user_id=demo_user.id,
                sender="assistant",
                content="Welcome to your Autumn Eco Blazer project! I've loaded your reference analysis. Based on your stiff twill texture, Organic Hemp or Heavy Linen Twill are ideal replacements.",
                metadata_json={}
            )
            db.add(chat_msg)
            db.commit()

        # Seed initial standalone fabric detection records for testing demo
        existing_detection = db.query(FabricAnalysis).filter(FabricAnalysis.detected_fabric == "Cotton").first()
        if not existing_detection:
            sample_analyses = [
                FabricAnalysis(
                    user_id=demo_user.id,
                    image_url="/static/uploads/demo/cotton_tshirt.jpg",
                    garment_type="shirt",
                    garment_category="shirt",
                    detected_fabric="Cotton",
                    fabric_type="Cotton",
                    confidence_score=0.88,
                    alternative_possible_fabrics=[
                        {"name": "Organic cotton", "confidence": 0.76},
                        {"name": "Linen", "confidence": 0.62}
                    ],
                    texture="smooth",
                    weave_or_knit_type="jersey",
                    pattern="solid",
                    dominant_colors=[
                        {"hex": "#2F4F4F", "name": "Dark Slate Gray", "percentage": 65},
                        {"hex": "#E8DCC4", "name": "Cream", "percentage": 35}
                    ],
                    secondary_colors=[{"hex": "#E8DCC4", "name": "Cream", "percentage": 35}],
                    material_properties={
                        "thickness": "light",
                        "stretch": "medium",
                        "shine": "matte",
                        "opacity": "opaque",
                        "drape": "moderate"
                    },
                    sustainability_note="This result is AI-estimated from visual appearance and should be confirmed through physical testing.",
                    is_user_corrected=False
                ),
                FabricAnalysis(
                    user_id=demo_user.id,
                    image_url="/static/uploads/demo/linen_dress.jpg",
                    garment_type="dress",
                    garment_category="dress",
                    detected_fabric="Linen",
                    fabric_type="Linen",
                    confidence_score=0.86,
                    alternative_possible_fabrics=[
                        {"name": "Hemp", "confidence": 0.72},
                        {"name": "Organic cotton", "confidence": 0.64}
                    ],
                    texture="rough",
                    weave_or_knit_type="plain weave",
                    pattern="solid",
                    dominant_colors=[
                        {"hex": "#E8DCC4", "name": "Cream", "percentage": 70},
                        {"hex": "#556B2F", "name": "Olive Green", "percentage": 30}
                    ],
                    secondary_colors=[{"hex": "#556B2F", "name": "Olive Green", "percentage": 30}],
                    material_properties={
                        "thickness": "medium",
                        "stretch": "low",
                        "shine": "matte",
                        "opacity": "opaque",
                        "drape": "structured"
                    },
                    sustainability_note="This result is AI-estimated from visual appearance and should be confirmed through physical testing.",
                    is_user_corrected=False
                ),
                FabricAnalysis(
                    user_id=demo_user.id,
                    image_url="/static/uploads/demo/denim_jacket.jpg",
                    garment_type="trousers",
                    garment_category="trousers",
                    detected_fabric="Denim",
                    fabric_type="Denim",
                    confidence_score=0.92,
                    alternative_possible_fabrics=[
                        {"name": "Cotton", "confidence": 0.81},
                        {"name": "Recycled polyester", "confidence": 0.58}
                    ],
                    texture="woven",
                    weave_or_knit_type="twill",
                    pattern="solid",
                    dominant_colors=[
                        {"hex": "#191970", "name": "Midnight Blue", "percentage": 80},
                        {"hex": "#708090", "name": "Slate Gray", "percentage": 20}
                    ],
                    secondary_colors=[{"hex": "#708090", "name": "Slate Gray", "percentage": 20}],
                    material_properties={
                        "thickness": "heavy",
                        "stretch": "low",
                        "shine": "matte",
                        "opacity": "opaque",
                        "drape": "structured"
                    },
                    sustainability_note="This result is AI-estimated from visual appearance and should be confirmed through physical testing.",
                    is_user_corrected=False
                )
            ]
            db.add_all(sample_analyses)
            db.commit()

        # Seed ModelVersion if none exists
        from app.models.models import ModelVersion
        from app.ml.model_evaluator import generate_default_evaluation_metrics
        
        existing_model = db.query(ModelVersion).filter(ModelVersion.version == "v2.4-EfficientNetV2").first()
        if not existing_model:
            metrics_data = generate_default_evaluation_metrics()
            init_model = ModelVersion(
                version=metrics_data["version"],
                model_name=metrics_data["model_name"],
                dataset_size=metrics_data["dataset_size"],
                physical_samples_count=metrics_data["physical_samples_count"],
                accuracy=metrics_data["accuracy"],
                macro_f1=metrics_data["macro_f1"],
                precision=metrics_data["precision"],
                recall=metrics_data["recall"],
                confusion_matrix=metrics_data["confusion_matrix"],
                class_metrics=metrics_data["class_metrics"],
                condition_metrics=metrics_data["condition_metrics"],
                is_active=True
            )
            db.add(init_model)
            db.commit()

        print("Database seed successful!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
