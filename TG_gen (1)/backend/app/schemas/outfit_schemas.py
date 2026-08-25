"""
Pydantic schemas for the AI Outfit Studio feature.
Updated for Pydantic V2 compatibility with support for Indian retailers,
multi-variation images, and verified shopping search links.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ─────────────────────────────────────────────────────────────────────────────
# Request
# ─────────────────────────────────────────────────────────────────────────────

class OutfitGenerateRequest(BaseModel):
    scenario: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Occasion / scenario description, e.g. 'College farewell party'",
        json_schema_extra={"example": "Eco-friendly college farewell outfit for women"},
    )
    gender_preference: Optional[str] = Field(
        None,
        description="women | men | unisex | no_preference",
        json_schema_extra={"example": "women"},
    )
    budget_inr: Optional[float] = Field(
        None, ge=200, le=500_000,
        description="Maximum total budget in Indian Rupees",
        json_schema_extra={"example": 5000},
    )
    is_budget_friendly: Optional[bool] = Field(None, description="Prioritize high-value budget-friendly pieces and thrift alternatives")
    budget_tier: Optional[str] = Field(None, description="budget_friendly | balanced | premium")
    size: Optional[str] = Field(None, json_schema_extra={"example": "M"})
    location: Optional[str] = Field(None, json_schema_extra={"example": "India"})
    weather_season: Optional[str] = Field(None, json_schema_extra={"example": "summer"})
    preferred_colors: Optional[List[str]] = Field(default_factory=list, json_schema_extra={"example": ["sage green", "cream"]})
    preferred_fabrics: Optional[List[str]] = Field(default_factory=list, json_schema_extra={"example": ["Tencel", "organic cotton"]})
    sustainability_preferences: Optional[List[str]] = Field(
        default_factory=list,
        json_schema_extra={"example": ["low water impact", "vegan"]},
    )
    style: Optional[str] = Field(
        None,
        description="casual | formal | traditional | party | streetwear | minimal | luxury",
        json_schema_extra={"example": "party"},
    )
    reference_image_path: Optional[str] = Field(None, description="Server-side path of an uploaded reference image")

    @field_validator("scenario")
    @classmethod
    def scenario_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("scenario must not be blank")
        return v.strip()

    @field_validator("gender_preference")
    @classmethod
    def valid_gender(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"women", "men", "unisex", "no_preference", None}
        if v and v.lower() not in allowed:
            raise ValueError(f"gender_preference must be one of {allowed - {None}}")
        return v.lower() if v else v

    @field_validator("style")
    @classmethod
    def valid_style(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"casual", "formal", "traditional", "party", "streetwear", "minimal", "luxury", None}
        if v and v.lower() not in allowed:
            raise ValueError(f"style must be one of {allowed - {None}}")
        return v.lower() if v else v


# ─────────────────────────────────────────────────────────────────────────────
# Outfit item
# ─────────────────────────────────────────────────────────────────────────────

class OutfitItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    category: str = Field(..., json_schema_extra={"example": "Dress"})
    name: str = Field(..., json_schema_extra={"example": "Sage green wrap midi dress"})
    search_query: Optional[str] = Field(
        None,
        json_schema_extra={"example": "women sage green wrap midi dress formal office"},
    )
    preferred_fabric: Optional[str] = Field(None, json_schema_extra={"example": "Tencel or linen blend"})
    recommended_fabric: Optional[str] = Field(None, json_schema_extra={"example": "Tencel/Lyocell"})
    color: Optional[str] = Field(None, json_schema_extra={"example": "Sage green"})
    estimated_budget_inr: Optional[float] = Field(None, json_schema_extra={"example": 3500.0})
    is_budget_friendly: Optional[bool] = Field(None, description="Prioritize high-value budget-friendly pieces and thrift alternatives")
    budget_tier: Optional[str] = Field(None, description="budget_friendly | balanced | premium")
    estimated_price_inr: Optional[float] = Field(None, json_schema_extra={"example": 3500.0})
    sustainability_note: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Full outfit concept
# ─────────────────────────────────────────────────────────────────────────────

class OutfitSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    outfit_name: str
    occasion: Optional[str] = None
    description: str
    items: List[OutfitItemSchema] = []
    color_palette: List[str] = []          # hex codes or colour names
    recommended_fabrics: List[str] = []
    sustainability_summary: Optional[str] = None
    sustainability_score: Optional[int] = Field(None, ge=0, le=100)
    styling_tips: List[str] = []
    total_estimated_price_inr: Optional[float] = None


# ─────────────────────────────────────────────────────────────────────────────
# Generated outfit image and variations
# ─────────────────────────────────────────────────────────────────────────────

IMAGE_DISCLAIMER = "AI-generated style concept — not an exact purchasable product."
DEMO_IMAGE_MESSAGE = "Live outfit-image generation is not configured. Showing a demo concept."
STORE_VERIFICATION_NOTICE = "Prices, stock, sizes, and fabric details are verified on the retailer website."

class GeneratedImageInfo(BaseModel):
    url: Optional[str] = None
    status: str = "demo"                   # generated | demo | unavailable
    disclaimer: str = IMAGE_DISCLAIMER
    message: Optional[str] = None
    prompt: Optional[str] = None


class GeneratedOutfitImageVariationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    variation_index: int = 1
    variation_title: str = "Editorial Concept View"
    image_url: str
    status: str = "demo"                   # generated | demo | unavailable
    label: str = IMAGE_DISCLAIMER
    prompt: Optional[str] = None
    created_at: Optional[datetime] = None


class GeneratedOutfitImageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    generation_id: int
    image_url: str
    generation_mode: str = "mock"
    label: str = IMAGE_DISCLAIMER
    created_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Retailer search links
# ─────────────────────────────────────────────────────────────────────────────

class RetailerSearchLinkSchema(BaseModel):
    retailer: str                          # Myntra | AJIO | Nykaa Fashion | Amazon India | Tata CLiQ | etc.
    search_url: str
    query: str
    icon: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Shopping match (product result)
# ─────────────────────────────────────────────────────────────────────────────

class ShoppingMatchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    retailer: str = "Myntra"               # Myntra | AJIO | Nykaa Fashion | Amazon India | Tata CLiQ | Official Brand
    category: Optional[str] = None
    title: str
    brand: Optional[str] = None
    price_inr: Optional[float] = None
    price: Optional[float] = None          # Backwards compat
    currency: str = "INR"
    product_url: str
    image_url: Optional[str] = None
    fabric_details: Optional[str] = None
    available_sizes: List[str] = []
    match_score: float = Field(0.0, ge=0.0, le=1.0)
    data_source: str = "affiliate_feed"    # affiliate_feed | official_api | approved_search | mock_demo
    source_type: str = "authorized_retailer"# official_brand | authorized_retailer | marketplace | mock_demo
    status: str = "verified"               # verified | demo
    timestamp: Optional[str] = None
    sustainability_label: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Main response
# ─────────────────────────────────────────────────────────────────────────────

SHOPPING_DISCLAIMER = (
    "Shopping matches are AI-curated similar product suggestions. "
    "Prices, stock, sizes, and fabric details are verified on the retailer website. "
    "Confirm price, stock, size, fabric composition, shipping, and return policy "
    "directly on the seller's website before purchasing. "
    "EcoFabric is not affiliated with any listed retailer."
)

class OutfitGenerateResponse(BaseModel):
    generation_id: int
    outfit: OutfitSchema
    generated_image: GeneratedImageInfo
    generated_images: List[GeneratedOutfitImageVariationSchema] = []
    generated_image_url: Optional[str] = None
    generated_image_id: Optional[int] = None
    image_label: str = IMAGE_DISCLAIMER
    shopping_results: List[ShoppingMatchSchema] = []
    shopping_matches: List[ShoppingMatchSchema] = []  # Backwards compat alias
    retailer_search_links: List[RetailerSearchLinkSchema] = []
    provider_info: Dict[str, str] = {}
    disclaimer: str = SHOPPING_DISCLAIMER
    store_verification_notice: str = STORE_VERIFICATION_NOTICE
    is_mock_mode: bool = True
    gender_preference: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Saved outfit
# ─────────────────────────────────────────────────────────────────────────────

class SaveOutfitRequest(BaseModel):
    project_id: Optional[int] = None
    notes: Optional[str] = None


class SavedOutfitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    generation_id: int
    project_id: Optional[int] = None
    notes: Optional[str] = None
    saved_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# History list item
# ─────────────────────────────────────────────────────────────────────────────

class OutfitHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    generation_id: int
    outfit_name: Optional[str] = None
    scenario: str
    style: Optional[str] = None
    gender_preference: Optional[str] = None
    budget_inr: Optional[float] = None
    total_estimated_price_inr: Optional[float] = None
    generated_image_url: Optional[str] = None
    sustainability_score: Optional[int] = None
    created_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Product Comparison & Buying Similar Styles Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ProductResult(BaseModel):
    """Canonical structure for real fashion products matched with outfit items."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique product ID")
    outfit_item: str = Field(..., description="Target outfit item name (e.g., 'Sage green wrap midi dress')")
    title: str = Field(..., description="Verified product title")
    retailer: str = Field(..., description="Retail store name (e.g., 'Myntra', 'AJIO', 'Nykaa Fashion')")
    product_url: str = Field(..., description="Verified official or affiliate URL")
    image_url: Optional[str] = Field(None, description="Verified product image URL")
    current_price_inr: Optional[float] = Field(None, description="Current price in INR")
    original_price_inr: Optional[float] = Field(None, description="Original price before discount in INR")
    discount_percent: Optional[float] = Field(None, description="Discount percentage")
    fabric_details: Optional[str] = Field(None, description="Fabric details if provided by retailer")
    sustainability_details: Optional[str] = Field(None, description="Verified sustainability information")
    match_score: float = Field(0.0, ge=0.0, le=1.0, description="Match score (0.0 - 1.0)")
    data_source: str = Field("approved_affiliate_feed", description="Source of product data")
    status: str = Field("verified", description="verified | demo")
    last_updated_at: str = Field(..., description="ISO timestamp of last price/data check")


class BestDealInfo(BaseModel):
    best_price_product: Optional[ProductResult] = None
    best_sustainable_product: Optional[ProductResult] = None
    estimated_savings_inr: Optional[float] = None
    next_cheapest_price_inr: Optional[float] = None
    verified_source_label: str = "Verified Live Feed"
    has_verified_savings: bool = False


class PriceComparisonResponse(BaseModel):
    outfit_item: Optional[str] = None
    total_products: int = 0
    best_deal: Optional[BestDealInfo] = None
    products: List[ProductResult] = []
    retailer_fallback_links: List[RetailerSearchLinkSchema] = []
    is_demo_mode: bool = True
    disclaimer: str = (
        "Prices, stock, sizes, and fabric details are verified on the retailer website. "
        "Confirm price, stock, size, fabric composition, shipping, and return policy directly on the seller's website."
    )


class ProductSearchRequest(BaseModel):
    items: Optional[List[Dict[str, Any]]] = None
    outfit_item_name: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    style: Optional[str] = None
    color: Optional[str] = None
    fabric: Optional[str] = None
    occasion: Optional[str] = None
    budget_inr: Optional[float] = None
    is_budget_friendly: Optional[bool] = None
    budget_tier: Optional[str] = None
    location: Optional[str] = "India"
    retailer_filter: Optional[str] = "All Stores"
    limit: int = 12


class ProductSaveRequest(BaseModel):
    product: ProductResult
    notes: Optional[str] = None


class ProductSaveResponse(BaseModel):
    id: int
    product_id: str
    title: str
    retailer: str
    saved_at: datetime
    message: str = "Product saved to your profile."


class PriceAlertCreateRequest(BaseModel):
    product_id: str
    product_title: str
    product_url: str
    retailer: str
    target_price_inr: float = Field(..., gt=0, description="Target price in INR to trigger alert")
    initial_price_inr: Optional[float] = None
    current_price_inr: Optional[float] = None


class PriceAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: str
    product_title: str
    retailer: str
    target_price_inr: float
    current_price_inr: Optional[float] = None
    is_active: bool
    is_triggered: bool
    created_at: datetime
    message: str = "Price alert configured successfully."


class PriceSnapshot(BaseModel):
    price_inr: float
    original_price_inr: Optional[float] = None
    is_verified: bool = True
    recorded_at: str


class PriceHistoryResponse(BaseModel):
    product_id: str
    retailer: Optional[str] = None
    current_price_inr: Optional[float] = None
    lowest_price_inr: Optional[float] = None
    highest_price_inr: Optional[float] = None
    snapshots: List[PriceSnapshot] = []
    has_history: bool = False
    message: str = "Price history will appear after we collect verified price updates."


class RetailerCouponSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    retailer: str
    coupon_code: str
    discount_text: str
    terms: Optional[str] = None
    expiry_date: Optional[str] = None
    source: str = "approved_affiliate"
    is_verified: bool = True

