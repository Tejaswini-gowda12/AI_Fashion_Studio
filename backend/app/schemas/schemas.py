from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth & User ---
class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserResponse"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[str] = "user"
    sustainability_preferences: Optional[Dict[str, Any]] = None
    preferred_materials: Optional[List[str]] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    sustainability_preferences: Optional[Dict[str, Any]] = None
    preferred_materials: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    sustainability_preferences: Optional[Dict[str, Any]] = {}
    preferred_materials: Optional[List[str]] = []
    created_at: datetime

    class Config:
        from_attributes = True


# --- Project ---
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_garment_type: Optional[str] = None
    intended_season: Optional[str] = None
    target_audience: Optional[str] = None
    budget_range: Optional[str] = None
    sustainability_goal: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_garment_type: Optional[str] = None
    intended_season: Optional[str] = None
    target_audience: Optional[str] = None
    budget_range: Optional[str] = None
    sustainability_goal: Optional[str] = None

class ReferenceImageResponse(BaseModel):
    id: int
    project_id: int
    file_path: str
    original_filename: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    target_garment_type: Optional[str] = None
    intended_season: Optional[str] = None
    target_audience: Optional[str] = None
    budget_range: Optional[str] = None
    sustainability_goal: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reference_images: List[ReferenceImageResponse] = []

    class Config:
        from_attributes = True


# --- Fabric Analysis & Detection Schemas ---
class DominantColor(BaseModel):
    hex: str
    name: str
    percentage: int

class AlternativeFabric(BaseModel):
    name: str
    confidence: float

class MaterialProperties(BaseModel):
    thickness: str = "medium"  # light / medium / heavy
    stretch: str = "low"       # low / medium / high
    shine: str = "matte"       # matte / semi-gloss / glossy
    opacity: str = "opaque"    # sheer / semi-sheer / opaque
    drape: str = "moderate"    # structured / moderate / fluid

class FabricDetails(BaseModel):
    description: str
    fiber_origin: str
    weight_gsm: str
    water_footprint_liters_per_kg: str
    carbon_footprint_kg_per_kg: str
    biodegradability_time: str
    durability_rating: float
    breathability_level: str
    care_instructions: str
    certifications: List[str]
    best_applications: List[str]
    pros: List[str]
    cons: List[str]

class TopPredictionItem(BaseModel):
    fabric: str
    confidence: float

class VisibleFeatures(BaseModel):
    texture: str = "smooth"
    weave: str = "plain weave"
    pattern: str = "solid"
    thickness: str = "medium"
    shine: str = "matte"
    stretch: str = "low"
    opacity: str = "opaque"

class CheckDetail(BaseModel):
    passed: bool
    actual: Optional[str] = None
    required: Optional[str] = None
    message: str

class QualityChecks(BaseModel):
    resolution: CheckDetail
    blur: CheckDetail
    lighting: CheckDetail
    fabric_coverage: CheckDetail

class ImageQualityMetrics(BaseModel):
    # ── Structured (new) fields ──────────────────────────────────────────────
    is_valid: bool = True
    quality_score: int = 89            # 0-100 integer score
    checks: Optional[Dict[str, Any]] = None   # per-check pass/fail + messages
    user_guidance: List[str] = []
    # ── Backward-compatible flat aliases ─────────────────────────────────────
    score: Optional[float] = 0.89      # float 0-1  (quality_score / 100)
    blur: Optional[str] = "low"        # "low" / "medium" / "high"
    lighting: Optional[str] = "good"   # "good" / "under-exposed" / "over-exposed"
    fabric_coverage: Optional[float] = 0.83   # float 0-1
    min_resolution_passed: Optional[bool] = True
    warning: Optional[str] = None

class FabricAnalyzeResponse(BaseModel):
    id: Optional[int] = None
    predicted_fabric: str
    detected_fabric: Optional[str] = None
    # ── Confidence ─── both spellings exposed for compatibility ──────────────
    confidence: float = 0.89
    confidence_score: float = 0.89
    # ── Prediction status ─── both spellings exposed ──────────────────────────
    status: str = "high_confidence"
    prediction_status: str = "high_confidence"
    top_predictions: List[TopPredictionItem]
    # ── Rich explanation fields ───────────────────────────────────────────────
    explanation: str = "Visually consistent with material texture."
    visible_features: VisibleFeatures
    image_quality: Dict[str, Any]
    limitations: str
    recommended_next_step: str = "Check garment label or conduct physical test."
    fabric_details: Optional[Dict[str, Any]] = None
    user_corrected_fabric: Optional[str] = None
    is_user_corrected: Optional[bool] = False
    dominant_colors: Optional[List[Any]] = []
    material_properties: Optional[Dict[str, Any]] = {}
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

class FabricDetectionResult(BaseModel):
    garment_type: str
    detected_fabric: str
    alternative_possible_fabrics: List[AlternativeFabric]
    confidence_score: float
    texture: str
    weave_or_knit_type: str
    pattern: str
    dominant_colors: List[DominantColor]
    material_properties: MaterialProperties
    sustainability_note: str
    fabric_details: Optional[FabricDetails] = None
    # ── New rich-explanation fields ───────────────────────────────────────────
    explanation: Optional[str] = None
    top_predictions: Optional[List[TopPredictionItem]] = None

class FabricAnalysisCorrection(BaseModel):
    user_corrected_fabric: str
    garment_type: Optional[str] = None
    material_properties: Optional[MaterialProperties] = None

class FabricDetectionRecordResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    image_url: Optional[str] = ""
    garment_type: str = "fabric swatch"
    detected_fabric: str = "Cotton"
    confidence_score: float = 0.86
    alternative_possible_fabrics: List[Any] = []
    texture: str = "smooth"
    weave_or_knit_type: str = "plain weave"
    pattern: str = "solid"
    dominant_colors: List[Any] = []
    material_properties: Dict[str, Any] = {}
    sustainability_note: Optional[str] = None
    user_corrected_fabric: Optional[str] = None
    fabric_details: Optional[Dict[str, Any]] = None
    image_quality: Optional[Dict[str, Any]] = None
    top_predictions: Optional[List[Dict[str, Any]]] = None
    prediction_status: Optional[str] = "high_confidence"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PredictionFeedbackCreate(BaseModel):
    analysis_id: Optional[int] = None
    predicted_fabric: str
    corrected_fabric: str
    verified_composition: Optional[str] = None
    physical_test_method: Optional[str] = None
    image_quality_rating: Optional[int] = 5
    feedback_notes: Optional[str] = None

class PredictionFeedbackResponse(BaseModel):
    id: int
    analysis_id: Optional[int] = None
    user_id: Optional[int] = None
    predicted_fabric: str
    corrected_fabric: str
    verified_composition: Optional[str] = None
    physical_test_method: Optional[str] = None
    image_quality_rating: int = 5
    feedback_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ModelVersionResponse(BaseModel):
    id: int
    version: str
    model_name: str
    dataset_size: int
    physical_samples_count: int
    accuracy: float
    macro_f1: float
    precision: float
    recall: float
    confusion_matrix: List[List[int]]
    class_metrics: Dict[str, Any]
    condition_metrics: Dict[str, Any]
    is_active: bool
    evaluation_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ModelMetricsResponse(BaseModel):
    active_model: ModelVersionResponse
    all_versions: List[ModelVersionResponse]
    dataset_stats: Dict[str, Any]

class TrainModelRequest(BaseModel):
    model_name: Optional[str] = "EfficientNetV2"
    epochs: Optional[int] = 10
    learning_rate: Optional[float] = 0.001
    temperature_scaling: Optional[bool] = True

class TrainModelResponse(BaseModel):
    status: str
    message: str
    new_version: Optional[ModelVersionResponse] = None

class FabricAnalysisResponse(BaseModel):
    id: int
    reference_image_id: Optional[int] = None
    garment_category: str
    fabric_type: str
    dominant_colors: List[Any] = []
    secondary_colors: List[Any] = []
    pattern_type: str
    weave: str
    shine: str
    thickness: str
    stretch: str
    drape: str
    opacity: str
    confidence_score: float
    is_user_corrected: bool
    created_at: datetime

    class Config:
        from_attributes = True

class FabricAnalysisUpdate(BaseModel):
    garment_category: Optional[str] = None
    fabric_type: Optional[str] = None
    user_corrected_fabric: Optional[str] = None
    dominant_colors: Optional[List[Any]] = None
    secondary_colors: Optional[List[Any]] = None
    pattern_type: Optional[str] = None
    weave: Optional[str] = None
    shine: Optional[str] = None
    thickness: Optional[str] = None
    stretch: Optional[str] = None
    drape: Optional[str] = None
    opacity: Optional[str] = None


# --- Fabric Catalog ---
class FabricBase(BaseModel):
    name: str
    category: str
    fiber_source: str
    water_impact_score: int = 70
    carbon_impact_score: int = 70
    biodegradability_score: int = 80
    cost_level: str = "Medium"
    durability_rating: int = 4
    comfort_rating: int = 4
    is_vegan: bool = True
    is_recyclable: bool = True
    texture_tags: List[str] = []
    pros: List[str] = []
    limitations: List[str] = []
    best_use_cases: List[str] = []
    is_active: bool = True

class FabricCreate(FabricBase):
    pass

class FabricResponse(FabricBase):
    id: int

    class Config:
        from_attributes = True


# --- Dye Methods ---
class DyeMethodBase(BaseModel):
    name: str
    process_type: str
    water_impact_level: str = "Low"
    energy_impact_level: str = "Low"
    cost_level: str = "Medium"
    color_accuracy_rating: int = 4
    limitation_notes: Optional[str] = None
    suitable_fabrics: List[str] = []
    is_active: bool = True

class DyeMethodCreate(DyeMethodBase):
    pass

class DyeMethodResponse(DyeMethodBase):
    id: int

    class Config:
        from_attributes = True


# --- Recommendation Slider Weights ---
class PriorityWeights(BaseModel):
    lowest_cost: float = Field(0.5, ge=0.0, le=1.0)
    closest_appearance: float = Field(0.8, ge=0.0, le=1.0)
    low_water: float = Field(0.7, ge=0.0, le=1.0)
    low_carbon: float = Field(0.7, ge=0.0, le=1.0)
    recyclability: float = Field(0.6, ge=0.0, le=1.0)
    vegan: float = Field(0.0, ge=0.0, le=1.0)
    durability: float = Field(0.6, ge=0.0, le=1.0)

class RecommendationQuery(BaseModel):
    analysis_id: int
    weights: Optional[PriorityWeights] = Field(default_factory=PriorityWeights)

class FabricRecommendationResponse(BaseModel):
    fabric: FabricResponse
    match_percentage: float
    calculation_breakdown: Dict[str, Any]
    match_reasons: List[str]

    class Config:
        from_attributes = True


# --- Dyeing Suggestion Response ---
class DyeRecommendationResponse(BaseModel):
    dye_method: DyeMethodResponse
    compatibility: str
    color_accuracy: str
    water_impact: str
    energy_impact: str
    estimated_cost: str
    recommendation_rationale: str


# --- Environmental Impact ---
class ImpactCalculateRequest(BaseModel):
    analysis_id: int
    conventional_fabric_name: Optional[str] = "Conventional Cotton"
    selected_fabric_id: int
    conventional_dye_name: Optional[str] = "Conventional Synthetic Reactive Dye"
    selected_dye_id: int
    garment_weight_kg: Optional[float] = 0.5

class ImpactAssessmentResponse(BaseModel):
    analysis_id: int
    conventional_fabric: str
    selected_fabric: str
    conventional_dye: str
    selected_dye: str
    water_saved_liters: float
    co2_reduced_kg: float
    waste_reduced_kg: float
    chemical_reduction_pct: float
    summary_text: str
    assumptions: List[str]
    water_comparison: Dict[str, float]
    co2_comparison: Dict[str, float]

    class Config:
        from_attributes = True


# --- Chat & AI Assistant ---
class ChatMessageCreate(BaseModel):
    project_id: int
    content: str

class ChatMessageResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    sender: str
    content: str
    metadata_json: Optional[Dict[str, Any]] = {}
    created_at: datetime

    class Config:
        from_attributes = True


# --- Design Concepts ---
class DesignConceptCreate(BaseModel):
    project_id: int
    design_name: str
    inspiration_summary: Optional[str] = None
    silhouette: Optional[str] = None
    material_recommendation: Optional[str] = None
    color_palette: Optional[List[str]] = []
    dyeing_method: Optional[str] = None
    trims: Optional[str] = None
    sustainability_rationale: Optional[str] = None
    production_notes: Optional[str] = None

class DesignConceptResponse(BaseModel):
    id: int
    project_id: int
    design_name: str
    inspiration_summary: Optional[str] = None
    silhouette: Optional[str] = None
    material_recommendation: Optional[str] = None
    color_palette: List[str] = []
    dyeing_method: Optional[str] = None
    trims: Optional[str] = None
    sustainability_rationale: Optional[str] = None
    production_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Generated Concept Images ---
class GeneratedImageRequest(BaseModel):
    project_id: int
    concept_id: Optional[int] = None
    custom_prompt_suffix: Optional[str] = ""

class GeneratedImageResponse(BaseModel):
    id: int
    concept_id: Optional[int] = None
    project_id: int
    prompt: str
    image_url: str
    generation_mode: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Visual Search Schemas
# ─────────────────────────────────────────────────────────────────────────────

class VisualSearchMatchResponse(BaseModel):
    """A single web visual-match result returned to the frontend."""
    id: Optional[int] = None
    title: Optional[str] = None
    source_url: str
    thumbnail_url: Optional[str] = None
    source_domain: Optional[str] = None
    match_score: float = 0.0
    detected_product_type: Optional[str] = None
    # Explicitly stated fabric info from source page — None if not found
    fabric_text_found: Optional[str] = None
    brand: Optional[str] = None
    price_text: Optional[str] = None
    # Reliability: official_brand | retailer | blog_editorial | unknown
    source_reliability: str = "unknown"
    # Verification: source_text_found | not_verified
    verification_status: str = "not_verified"

    class Config:
        from_attributes = True


class VisualSearchQueryContext(BaseModel):
    """The AI-derived context that was used to guide the web search query."""
    ai_predicted_fabric: Optional[str] = None
    garment_type: Optional[str] = None


class VisualSearchResponse(BaseModel):
    """
    Full response from POST /api/visual-search/search.
    Always includes a disclaimer emphasising that matches are NOT fabric confirmation.
    """
    search_id: Optional[int] = None
    search_status: str  # success | failed | no_results
    provider_used: str = "mock"
    query_context: VisualSearchQueryContext
    matches: List[VisualSearchMatchResponse] = []
    related_entities: List[str] = []
    disclaimer: str = (
        "Web matches identify visually similar items only. "
        "Fabric composition must be verified through the product label, "
        "product page, or supplier specification sheet."
    )


class SaveMatchRequest(BaseModel):
    """Request body to save a web match to the user's saved items."""
    visual_search_match_id: Optional[int] = None
    project_id: Optional[int] = None
    # Denormalised snapshot fields (in case the match record is unavailable)
    title: Optional[str] = None
    source_url: str
    thumbnail_url: Optional[str] = None
    source_domain: Optional[str] = None
    source_reliability: Optional[str] = "unknown"
    fabric_text_found: Optional[str] = None
    match_score: Optional[float] = 0.0


class SavedWebMatchResponse(BaseModel):
    """A previously saved web match record."""
    id: int
    user_id: Optional[int] = None
    visual_search_match_id: Optional[int] = None
    project_id: Optional[int] = None
    title: Optional[str] = None
    source_url: str
    thumbnail_url: Optional[str] = None
    source_domain: Optional[str] = None
    source_reliability: str = "unknown"
    fabric_text_found: Optional[str] = None
    match_score: float = 0.0
    saved_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# AI Outfit Studio Schemas
# ─────────────────────────────────────────────────────────────────────────────

class OutfitGenerateRequest(BaseModel):
    """Input payload for POST /api/outfit/generate."""
    scenario: str = Field(..., min_length=5, max_length=1000,
                         description="User scenario, e.g. 'I need an outfit for a college farewell party'")
    gender_preference: Optional[str] = Field(None, description="women | men | unisex | no_preference")
    budget_inr: Optional[float] = Field(None, ge=100, le=1_000_000, description="Budget in INR")
    size: Optional[str] = Field(None, description="XS | S | M | L | XL | XXL or numeric")
    location: Optional[str] = Field(None, description="City or country, e.g. 'India', 'Mumbai'")
    weather_season: Optional[str] = Field(None, description="summer | winter | monsoon | spring | all-season")
    preferred_colors: Optional[List[str]] = Field(default_factory=list)
    preferred_fabrics: Optional[List[str]] = Field(default_factory=list)
    sustainability_preferences: Optional[List[str]] = Field(
        default_factory=list,
        description="vegan | recycled | organic | low-cost | low-water-impact"
    )
    style: Optional[str] = Field(None, description="casual | formal | traditional | party | streetwear | minimal | luxury")
    reference_image_url: Optional[str] = Field(None, description="Optional URL of an uploaded reference image")


class OutfitItemSchema(BaseModel):
    """A single garment or accessory item in the generated outfit."""
    category: str                              # Dress | Top | Bottom | Jacket | Footwear | Bag | Accessory
    name: str
    recommended_fabric: Optional[str] = None
    color: Optional[str] = None
    estimated_price_inr: Optional[float] = None
    sustainability_note: Optional[str] = None

    class Config:
        from_attributes = True


class OutfitSchema(BaseModel):
    """Full AI-generated outfit concept."""
    outfit_name: str
    occasion: Optional[str] = None
    description: str
    items: List[OutfitItemSchema] = []
    color_palette: List[str] = []              # hex codes
    recommended_fabrics: List[str] = []
    sustainability_summary: str
    sustainability_score: Optional[int] = None # 0-100
    styling_tips: List[str] = []
    total_estimated_price_inr: Optional[float] = None


class ShoppingMatchSchema(BaseModel):
    """A single shopping product result returned for an outfit item."""
    id: Optional[int] = None
    category: Optional[str] = None
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"
    product_url: str
    image_url: Optional[str] = None
    fabric_details: Optional[str] = None
    available_sizes: List[str] = []
    match_score: float = 0.0
    # official_brand | authorized_retailer | marketplace | mock_demo
    source_type: str = "mock_demo"
    # Only set when the product page explicitly states sustainability info
    sustainability_label: Optional[str] = None

    class Config:
        from_attributes = True


SHOPPING_DISCLAIMER = (
    "Shopping matches are similar product suggestions for inspiration only. "
    "Confirm price, stock, size, fabric composition, shipping, and return policy "
    "on the seller's website before purchasing. "
    "EcoFabric is not affiliated with any retailer. External links open the retailer's website."
)


class OutfitGenerateResponse(BaseModel):
    """Full response from POST /api/outfit/generate."""
    generation_id: Optional[int] = None
    outfit: OutfitSchema
    generated_image_url: Optional[str] = None
    image_label: str = "AI-generated style concept"
    image_generation_mode: str = "mock"
    shopping_matches: List[ShoppingMatchSchema] = []
    shopping_provider: str = "mock"
    llm_provider: str = "mock"
    demo_mode: bool = True
    disclaimer: str = SHOPPING_DISCLAIMER


class SaveOutfitRequest(BaseModel):
    generation_id: int
    project_id: Optional[int] = None
    notes: Optional[str] = None


class SavedOutfitResponse(BaseModel):
    """A previously saved outfit record (denormalised for easy display)."""
    id: int
    generation_id: int
    user_id: int
    project_id: Optional[int] = None
    notes: Optional[str] = None
    saved_at: datetime
    # Embedded outfit summary
    outfit_name: Optional[str] = None
    occasion: Optional[str] = None
    description: Optional[str] = None
    generated_image_url: Optional[str] = None
    total_estimated_price_inr: Optional[float] = None
    sustainability_score: Optional[int] = None

    class Config:
        from_attributes = True
