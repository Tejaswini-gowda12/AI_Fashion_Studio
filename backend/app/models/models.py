import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="user")  # user, admin
    sustainability_preferences = Column(JSON, default=dict)
    preferred_materials = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_garment_type = Column(String, nullable=True)
    intended_season = Column(String, nullable=True)
    target_audience = Column(String, nullable=True)
    budget_range = Column(String, nullable=True)
    sustainability_goal = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    reference_images = relationship("ReferenceImage", back_populates="project", cascade="all, delete-orphan")
    design_concepts = relationship("DesignConcept", back_populates="project", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="project", cascade="all, delete-orphan")


class ReferenceImage(Base):
    __tablename__ = "reference_images"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="reference_images")
    analyses = relationship("FabricAnalysis", back_populates="reference_image", cascade="all, delete-orphan")


class FabricAnalysis(Base):
    __tablename__ = "fabric_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reference_image_id = Column(Integer, ForeignKey("reference_images.id"), nullable=True)
    image_url = Column(String, nullable=True)
    garment_type = Column(String, default="fabric swatch")
    garment_category = Column(String, nullable=True)  # Legacy alias
    detected_fabric = Column(String, nullable=False, default="Cotton")
    fabric_type = Column(String, nullable=True)  # Legacy alias
    confidence_score = Column(Float, default=0.86)
    alternative_possible_fabrics = Column(JSON, default=list)
    texture = Column(String, default="smooth")
    weave_or_knit_type = Column(String, default="plain weave")
    pattern = Column(String, default="solid")
    dominant_colors = Column(JSON, default=list)
    secondary_colors = Column(JSON, default=list)
    material_properties = Column(JSON, default=dict)

    # Legacy attributes for backward compatibility
    pattern_type = Column(String, default="Solid")
    weave = Column(String, default="Twill")
    shine = Column(String, default="Matte")
    thickness = Column(String, default="Medium")
    stretch = Column(String, default="Low")
    drape = Column(String, default="Moderate")
    opacity = Column(String, default="Opaque")

    sustainability_note = Column(Text, nullable=True)
    ai_note = Column(Text, nullable=True)
    is_user_corrected = Column(Boolean, default=False)
    user_corrected_fabric = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
    reference_image = relationship("ReferenceImage", back_populates="analyses")
    recommendations = relationship("FabricRecommendation", back_populates="analysis", cascade="all, delete-orphan")
    impact_assessments = relationship("ImpactAssessment", back_populates="analysis", cascade="all, delete-orphan")

    @property
    def fabric_details(self):
        from app.services.fabric_detection_service import get_fabric_details
        target_fab = self.user_corrected_fabric or self.detected_fabric or "Cotton"
        return get_fabric_details(target_fab)


class Fabric(Base):
    __tablename__ = "fabrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    fiber_source = Column(String, nullable=False)
    water_impact_score = Column(Integer, default=70)
    carbon_impact_score = Column(Integer, default=70)
    biodegradability_score = Column(Integer, default=80)
    cost_level = Column(String, default="Medium")
    durability_rating = Column(Integer, default=4)
    comfort_rating = Column(Integer, default=4)
    is_vegan = Column(Boolean, default=True)
    is_recyclable = Column(Boolean, default=True)
    texture_tags = Column(JSON, default=list)
    pros = Column(JSON, default=list)
    limitations = Column(JSON, default=list)
    best_use_cases = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)


class DyeMethod(Base):
    __tablename__ = "dye_methods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    process_type = Column(String, nullable=False)
    water_impact_level = Column(String, default="Very Low")
    energy_impact_level = Column(String, default="Low")
    cost_level = Column(String, default="Medium")
    color_accuracy_rating = Column(Integer, default=4)
    limitation_notes = Column(Text, nullable=True)
    suitable_fabrics = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)


class FabricRecommendation(Base):
    __tablename__ = "fabric_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("fabric_analyses.id"), nullable=False)
    fabric_id = Column(Integer, ForeignKey("fabrics.id"), nullable=False)
    match_percentage = Column(Float, nullable=False)
    calculation_breakdown = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("FabricAnalysis", back_populates="recommendations")
    fabric = relationship("Fabric")


class ImpactAssessment(Base):
    __tablename__ = "impact_assessments"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("fabric_analyses.id"), nullable=False)
    conventional_fabric_id = Column(Integer, ForeignKey("fabrics.id"), nullable=True)
    selected_fabric_id = Column(Integer, ForeignKey("fabrics.id"), nullable=False)
    conventional_dye_id = Column(Integer, ForeignKey("dye_methods.id"), nullable=True)
    selected_dye_id = Column(Integer, ForeignKey("dye_methods.id"), nullable=False)
    
    water_saved_liters = Column(Float, default=0.0)
    co2_reduced_kg = Column(Float, default=0.0)
    waste_reduced_kg = Column(Float, default=0.0)
    chemical_reduction_pct = Column(Float, default=0.0)
    summary_text = Column(Text, nullable=True)
    assumptions_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("FabricAnalysis", back_populates="impact_assessments")
    selected_fabric = relationship("Fabric", foreign_keys=[selected_fabric_id])
    selected_dye = relationship("DyeMethod", foreign_keys=[selected_dye_id])


class DesignConcept(Base):
    __tablename__ = "design_concepts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    design_name = Column(String, nullable=False)
    inspiration_summary = Column(Text, nullable=True)
    silhouette = Column(String, nullable=True)
    material_recommendation = Column(String, nullable=True)
    color_palette = Column(JSON, default=list)
    dyeing_method = Column(String, nullable=True)
    trims = Column(String, nullable=True)
    sustainability_rationale = Column(Text, nullable=True)
    production_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="design_concepts")
    generated_images = relationship("GeneratedImage", back_populates="concept", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")


class GeneratedImage(Base):
    __tablename__ = "generated_images"

    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("design_concepts.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    image_url = Column(String, nullable=False)
    generation_mode = Column(String, default="mock")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    concept = relationship("DesignConcept", back_populates="generated_images")


class UploadedImage(Base):
    __tablename__ = "uploaded_images"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    blur_score = Column(Float, default=100.0)
    lighting_status = Column(String, default="good")
    fabric_coverage = Column(Float, default=0.85)
    quality_score = Column(Float, default=0.90)
    is_valid_quality = Column(Boolean, default=True)
    quality_warning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, nullable=False)
    model_name = Column(String, nullable=False, default="EfficientNetV2")
    dataset_size = Column(Integer, default=19000)
    physical_samples_count = Column(Integer, default=1900)
    accuracy = Column(Float, default=0.954)
    macro_f1 = Column(Float, default=0.948)
    precision = Column(Float, default=0.951)
    recall = Column(Float, default=0.946)
    confusion_matrix = Column(JSON, default=list)
    class_metrics = Column(JSON, default=dict)
    condition_metrics = Column(JSON, default=dict)
    checkpoint_path = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    evaluation_date = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PredictionFeedback(Base):
    __tablename__ = "prediction_feedback"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("fabric_analyses.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    predicted_fabric = Column(String, nullable=False)
    corrected_fabric = Column(String, nullable=False)
    verified_composition = Column(String, nullable=True)
    physical_test_method = Column(String, nullable=True)
    image_quality_rating = Column(Integer, default=5)
    feedback_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class TrainingDataset(Base):
    __tablename__ = "training_datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    total_images = Column(Integer, default=19000)
    physical_samples_count = Column(Integer, default=1900)
    train_split = Column(Float, default=0.70)
    val_split = Column(Float, default=0.15)
    test_split = Column(Float, default=0.15)
    class_distribution = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class FabricClass(Base):
    __tablename__ = "fabric_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    fiber_origin = Column(String, nullable=False)
    weight_gsm = Column(String, default="140 - 200 GSM")
    water_footprint_liters_per_kg = Column(String, default="5,000 L/kg")
    carbon_footprint_kg_per_kg = Column(String, default="3.0 kg CO2e/kg")
    biodegradability_time = Column(String, default="3 months")
    durability_rating = Column(Float, default=4.0)
    breathability_level = Column(String, default="High")
    care_instructions = Column(Text, default="Machine wash warm")
    certifications = Column(JSON, default=list)
    best_applications = Column(JSON, default=list)
    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)


# ─────────────────────────────────────────────────────────────────────────────
# Visual Search Models
# ─────────────────────────────────────────────────────────────────────────────

class VisualSearch(Base):
    """Records each web visual search request made by a user."""
    __tablename__ = "visual_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Reference to the uploaded image used for the search
    uploaded_image_path = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    # AI context at the time of search
    ai_predicted_fabric = Column(String, nullable=True)
    garment_type = Column(String, nullable=True)
    # Provider used (mock, google_vision, bing)
    provider_used = Column(String, nullable=False, default="mock")
    # Search outcome
    search_status = Column(String, default="success")  # success | failed | no_results
    total_matches_returned = Column(Integer, default=0)
    related_entities = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    matches = relationship("VisualSearchMatch", back_populates="visual_search", cascade="all, delete-orphan")


class VisualSearchMatch(Base):
    """One returned web visual match result from a visual search."""
    __tablename__ = "visual_search_matches"

    id = Column(Integer, primary_key=True, index=True)
    visual_search_id = Column(Integer, ForeignKey("visual_searches.id"), nullable=False)
    # Core match data
    title = Column(String, nullable=True)
    source_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    source_domain = Column(String, nullable=True)
    match_score = Column(Float, default=0.0)  # 0.0–1.0
    # Product information extracted from the source page
    detected_product_type = Column(String, nullable=True)
    fabric_text_found = Column(Text, nullable=True)  # null if not found
    brand = Column(String, nullable=True)
    price_text = Column(String, nullable=True)
    # Reliability classification: official_brand | retailer | blog_editorial | unknown
    source_reliability = Column(String, default="unknown")
    # Verification: source_text_found | not_verified
    verification_status = Column(String, default="not_verified")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    visual_search = relationship("VisualSearch", back_populates="matches")
    saved_by = relationship("SavedWebMatch", back_populates="match", cascade="all, delete-orphan")


class SavedWebMatch(Base):
    """A web match that a user has saved as inspiration."""
    __tablename__ = "saved_web_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    visual_search_match_id = Column(Integer, ForeignKey("visual_search_matches.id"), nullable=True)
    # Optional link to a designer project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    # Denormalized snapshot so the saved record is self-contained if match is deleted
    title = Column(String, nullable=True)
    source_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    source_domain = Column(String, nullable=True)
    source_reliability = Column(String, default="unknown")
    fabric_text_found = Column(Text, nullable=True)
    match_score = Column(Float, default=0.0)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)

    match = relationship("VisualSearchMatch", back_populates="saved_by")


# ─────────────────────────────────────────────────────────────────────────────
# AI Outfit Studio Models
# ─────────────────────────────────────────────────────────────────────────────

class OutfitGeneration(Base):
    """Top-level record for each AI outfit generation request."""
    __tablename__ = "outfit_generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # User inputs
    scenario = Column(Text, nullable=False)
    gender_preference = Column(String, nullable=True)   # women | men | unisex | no_preference
    budget_inr = Column(Float, nullable=True)
    size = Column(String, nullable=True)
    location = Column(String, nullable=True)
    weather_season = Column(String, nullable=True)
    preferred_colors = Column(JSON, default=list)
    preferred_fabrics = Column(JSON, default=list)
    sustainability_preferences = Column(JSON, default=list)
    style = Column(String, nullable=True)               # casual | formal | traditional | party | streetwear | minimal | luxury
    reference_image_path = Column(String, nullable=True)
    # AI-generated output
    outfit_name = Column(String, nullable=True)
    occasion = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    color_palette = Column(JSON, default=list)
    recommended_fabrics = Column(JSON, default=list)
    sustainability_summary = Column(Text, nullable=True)
    sustainability_score = Column(Integer, nullable=True)   # 0-100
    styling_tips = Column(JSON, default=list)
    total_estimated_price_inr = Column(Float, nullable=True)
    # Provider metadata
    llm_provider_used = Column(String, default="mock")
    image_provider_used = Column(String, default="mock")
    shopping_provider_used = Column(String, default="mock")
    generation_status = Column(String, default="success")  # success | failed | partial
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
    items = relationship("OutfitItem", back_populates="generation", cascade="all, delete-orphan")
    outfit_images = relationship("GeneratedOutfitImage", back_populates="generation", cascade="all, delete-orphan")
    shopping_searches = relationship("ShoppingSearch", back_populates="generation", cascade="all, delete-orphan")
    saved_by = relationship("SavedOutfit", back_populates="generation", cascade="all, delete-orphan")


class OutfitItem(Base):
    """Individual garment / accessory item within an outfit generation."""
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("outfit_generations.id"), nullable=False)
    category = Column(String, nullable=False)            # Dress | Top | Bottom | Jacket | Footwear | Bag | Accessory
    name = Column(String, nullable=False)
    recommended_fabric = Column(String, nullable=True)
    color = Column(String, nullable=True)
    estimated_price_inr = Column(Float, nullable=True)
    sustainability_note = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    generation = relationship("OutfitGeneration", back_populates="items")


class GeneratedOutfitImage(Base):
    """AI-generated outfit visualization image record."""
    __tablename__ = "generated_outfit_images"

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("outfit_generations.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    image_url = Column(String, nullable=False)          # data URI for SVG or remote URL
    generation_mode = Column(String, default="mock")    # mock | dalle | stablediffusion | gemini
    label = Column(String, default="AI-generated style concept")  # Always labelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    generation = relationship("OutfitGeneration", back_populates="outfit_images")


class ShoppingSearch(Base):
    """Records each shopping search session linked to an outfit generation."""
    __tablename__ = "shopping_searches"

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("outfit_generations.id"), nullable=False)
    query_context = Column(JSON, default=dict)          # category, style, color, budget used for search
    provider_used = Column(String, default="mock")
    search_status = Column(String, default="success")   # success | no_results | failed
    total_matches = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    generation = relationship("OutfitGeneration", back_populates="shopping_searches")
    matches = relationship("ShoppingMatch", back_populates="search", cascade="all, delete-orphan")


class ShoppingMatch(Base):
    """Individual shopping product result returned for an outfit item."""
    __tablename__ = "shopping_matches"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("shopping_searches.id"), nullable=False)
    category = Column(String, nullable=True)            # Maps to outfit item category
    title = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String, default="INR")
    product_url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    fabric_details = Column(String, nullable=True)
    available_sizes = Column(JSON, default=list)
    match_score = Column(Float, default=0.0)            # 0.0-1.0 textual + visual similarity
    source_type = Column(String, default="mock_demo")   # official_brand | authorized_retailer | marketplace | mock_demo
    sustainability_label = Column(String, nullable=True) # Only set if product page confirms it
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    search = relationship("ShoppingSearch", back_populates="matches")


class SavedOutfit(Base):
    """An outfit generation saved by a user to their profile."""
    __tablename__ = "saved_outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generation_id = Column(Integer, ForeignKey("outfit_generations.id"), nullable=False)
    # Optional link to a designer project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    notes = Column(Text, nullable=True)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)

    generation = relationship("OutfitGeneration", back_populates="saved_by")


class SavedProduct(Base):
    """A specific retail product match saved by a user to their wardrobe/wishlist."""
    __tablename__ = "saved_products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(String, index=True, nullable=False)
    outfit_item = Column(String, nullable=True)
    title = Column(String, nullable=False)
    retailer = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    current_price_inr = Column(Float, nullable=True)
    original_price_inr = Column(Float, nullable=True)
    discount_percent = Column(Float, nullable=True)
    fabric_details = Column(String, nullable=True)
    sustainability_details = Column(String, nullable=True)
    match_score = Column(Float, default=0.0)
    data_source = Column(String, default="approved_affiliate_feed")
    status = Column(String, default="verified")
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])


class ProductPriceHistory(Base):
    """Historical price snapshots collected for products."""
    __tablename__ = "product_price_histories"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, index=True, nullable=False)
    retailer = Column(String, nullable=False)
    price_inr = Column(Float, nullable=False)
    original_price_inr = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=True)
    source = Column(String, default="verified_feed")
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)


class PriceAlert(Base):
    """User-configured price alert for a target product price."""
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(String, index=True, nullable=False)
    product_title = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    retailer = Column(String, nullable=False)
    target_price_inr = Column(Float, nullable=False)
    initial_price_inr = Column(Float, nullable=True)
    current_price_inr = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])


class RetailerCoupon(Base):
    """Verified discount coupons provided by approved retailer feeds."""
    __tablename__ = "retailer_coupons"

    id = Column(Integer, primary_key=True, index=True)
    retailer = Column(String, index=True, nullable=False)
    coupon_code = Column(String, nullable=False)
    discount_text = Column(String, nullable=False)
    terms = Column(Text, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    source = Column(String, default="approved_affiliate")
    is_verified = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

