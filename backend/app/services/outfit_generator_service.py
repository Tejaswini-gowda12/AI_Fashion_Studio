"""
AI Outfit Generator Service
============================
Orchestrates three sub-tasks for every outfit generation request:
  1. LLM outfit concept generation  (mock | gemini | openai)
  2. Outfit visualization images    (2-4 variations via OutfitImageService)
  3. Shopping search & store links  (Indian retailers via ShoppingSearchService)

All data is persisted to the database before returning.
"""
from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import (
    GeneratedOutfitImage,
    OutfitGeneration,
    OutfitItem,
    SavedOutfit,
    ShoppingMatch,
    ShoppingSearch,
)
from app.schemas.outfit_schemas import (
    DEMO_IMAGE_MESSAGE,
    IMAGE_DISCLAIMER,
    SHOPPING_DISCLAIMER,
    STORE_VERIFICATION_NOTICE,
    GeneratedImageInfo,
    GeneratedOutfitImageVariationSchema,
    OutfitGenerateRequest,
    OutfitGenerateResponse,
    OutfitHistoryItem,
    OutfitItemSchema,
    OutfitSchema,
    RetailerSearchLinkSchema,
    SavedOutfitResponse,
    ShoppingMatchSchema,
)
from app.services.outfit_image_service import get_outfit_image_service
from app.services.providers.outfit_mock_provider import select_outfit
from app.services.shopping_search_service import get_shopping_search_service, is_safe_url

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# In-memory rate limiter
# ─────────────────────────────────────────────────────────────────────────────

_rate_window: Dict[str, list] = defaultdict(list)


def _check_rate_limit(key: str, max_calls: int = 5, window_seconds: int = 60) -> bool:
    """Return True if the caller is within the allowed rate."""
    now = time.time()
    timestamps = _rate_window[key]
    _rate_window[key] = [t for t in timestamps if now - t < window_seconds]
    if len(_rate_window[key]) >= max_calls:
        return False
    _rate_window[key].append(now)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# LLM concept generators
# ─────────────────────────────────────────────────────────────────────────────

def _mock_generate_outfit_concept(request: OutfitGenerateRequest) -> Dict[str, Any]:
    """Return an outfit dict from the mock library with item search queries."""
    import re
    scenario_lower = (request.scenario or "").lower()
    has_men_token = bool(re.search(r"\b(men|mens|men's|man|male|gentleman|boy|boys)\b", scenario_lower))
    has_women_token = bool(re.search(r"\b(women|womens|women's|woman|female|lady|ladies|girl|girls)\b", scenario_lower))

    effective_gender = request.gender_preference
    if not effective_gender or effective_gender == "no_preference":
        if has_men_token and not has_women_token:
            effective_gender = "men"
        elif has_women_token and not has_men_token:
            effective_gender = "women"

    outfit_raw = select_outfit(
        scenario=request.scenario,
        style=request.style,
        gender=effective_gender,
        budget_inr=request.budget_inr,
        preferred_colors=request.preferred_colors,
    )
    if request.preferred_colors:
        outfit_raw["color_palette"] = (
            request.preferred_colors[:2] + outfit_raw.get("color_palette", [])
        )[:5]

    # Ensure items have search_query and preferred_fabric
    gender_prefix = f"{effective_gender} " if effective_gender and effective_gender != "no_preference" else ""
    for item in outfit_raw.get("items", []):
        cat = item.get("category", "")
        nm = item.get("name", "")
        color = item.get("color", "")
        fab = item.get("recommended_fabric", "")
        item["preferred_fabric"] = fab
        item["estimated_budget_inr"] = item.get("estimated_price_inr")
        item["search_query"] = f"{gender_prefix}{color} {nm} {request.scenario}".strip()

    return outfit_raw


def _gemini_generate_outfit_concept(request: OutfitGenerateRequest) -> Dict[str, Any]:
    """Call Gemini API to generate a structured outfit concept."""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        if not api_key:
            return _mock_generate_outfit_concept(request)

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are a sustainable fashion designer. Generate a complete outfit concept as valid JSON.

User request:
- Scenario: {request.scenario}
- Gender: {request.gender_preference or "no_preference"}
- Budget (INR): {request.budget_inr or "flexible"}
- Style: {request.style or "any"}
- Preferred colors: {", ".join(request.preferred_colors or []) or "any"}
- Preferred fabrics: {", ".join(request.preferred_fabrics or []) or "any"}
- Sustainability: {", ".join(request.sustainability_preferences or []) or "general"}
- Location: {request.location or "India"}
- Season: {request.weather_season or "any"}

Return ONLY a JSON object with this exact structure:
{{
  "outfit_name": "string",
  "occasion": "string",
  "description": "string",
  "items": [
    {{
      "category": "Dress|Top|Bottom|Jacket|Footwear|Bag|Accessory",
      "name": "string",
      "search_query": "women sage green wrap midi dress formal office",
      "preferred_fabric": "Tencel or linen blend",
      "recommended_fabric": "Tencel/Lyocell",
      "color": "color name or hex",
      "estimated_budget_inr": number,
      "estimated_price_inr": number,
      "sustainability_note": "string or null"
    }}
  ],
  "color_palette": ["#hex1", "#hex2", "#hex3"],
  "recommended_fabrics": ["fabric1", "fabric2"],
  "sustainability_summary": "string",
  "sustainability_score": number_0_to_100,
  "styling_tips": ["tip1", "tip2", "tip3"],
  "total_estimated_price_inr": number
}}
"""
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        logger.warning("Gemini outfit generation failed: %s — falling back to mock", e)
        return _mock_generate_outfit_concept(request)


def _openai_generate_outfit_concept(request: OutfitGenerateRequest) -> Dict[str, Any]:
    """Call OpenAI API to generate a structured outfit concept."""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        if not api_key:
            return _mock_generate_outfit_concept(request)

        client = OpenAI(api_key=api_key)
        prompt = f"""You are a sustainable fashion designer. Generate a complete outfit concept.

Scenario: {request.scenario}
Gender: {request.gender_preference or "no_preference"}
Budget (INR): {request.budget_inr or "flexible"}
Style: {request.style or "any"}
Preferred colors: {", ".join(request.preferred_colors or []) or "any"}
Preferred fabrics: {", ".join(request.preferred_fabrics or []) or "any"}
Sustainability: {", ".join(request.sustainability_preferences or []) or "general"}
Location: {request.location or "India"}
Season: {request.weather_season or "any"}

Return ONLY valid JSON with keys:
- outfit_name, occasion, description
- items: array with category, name, search_query, preferred_fabric, recommended_fabric, color, estimated_budget_inr, estimated_price_inr, sustainability_note
- color_palette, recommended_fabrics, sustainability_summary, sustainability_score (0-100), styling_tips, total_estimated_price_inr."""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=1500,
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        logger.warning("OpenAI outfit generation failed: %s — falling back to mock", e)
        return _mock_generate_outfit_concept(request)


def _generate_outfit_concept(request: OutfitGenerateRequest) -> tuple[Dict[str, Any], str]:
    """Dispatch to the configured LLM provider. Returns (outfit_dict, provider_name)."""
    provider = os.getenv("OUTFIT_LLM_PROVIDER", settings.OUTFIT_LLM_PROVIDER).lower()
    openai_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
    gemini_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY

    if provider == "gemini" and gemini_key and not gemini_key.startswith("AQ.placeholder"):
        return _gemini_generate_outfit_concept(request), "gemini"
    if provider == "openai" and openai_key and not openai_key.startswith("sk-proj-placeholder"):
        return _openai_generate_outfit_concept(request), "openai"
    return _mock_generate_outfit_concept(request), "mock"


# ─────────────────────────────────────────────────────────────────────────────
# Main Outfit Generator Service
# ─────────────────────────────────────────────────────────────────────────────

class OutfitGeneratorService:

    def generate(
        self,
        request: OutfitGenerateRequest,
        db: Session,
        user_id: Optional[int] = None,
        rate_limit_key: str = "global",
    ) -> OutfitGenerateResponse:
        """
        Orchestrate complete outfit generation:
        1. Rate limit verification
        2. LLM outfit concept generation
        3. Database persistence of generation & items
        4. 2-4 concept image variations via OutfitImageService
        5. Verified shopping search & Indian retailer search links via ShoppingSearchService
        """
        # 1. Rate limit check
        if not _check_rate_limit(
            rate_limit_key,
            max_calls=settings.OUTFIT_RATE_LIMIT_PER_MIN,
            window_seconds=60,
        ):
            raise RuntimeError("Rate limit exceeded. Please wait before generating another outfit.")

        # 2. Generate outfit concept
        outfit_raw, llm_provider = _generate_outfit_concept(request)

        # 3. Persist generation record
        generation = OutfitGeneration(
            user_id=user_id,
            scenario=request.scenario,
            gender_preference=request.gender_preference,
            budget_inr=request.budget_inr,
            size=request.size,
            location=request.location,
            weather_season=request.weather_season,
            preferred_colors=request.preferred_colors or [],
            preferred_fabrics=request.preferred_fabrics or [],
            sustainability_preferences=request.sustainability_preferences or [],
            style=request.style,
            reference_image_path=request.reference_image_path,
            outfit_name=outfit_raw.get("outfit_name", "Eco Outfit"),
            occasion=outfit_raw.get("occasion"),
            description=outfit_raw.get("description", ""),
            color_palette=outfit_raw.get("color_palette", []),
            recommended_fabrics=outfit_raw.get("recommended_fabrics", []),
            sustainability_summary=outfit_raw.get("sustainability_summary"),
            sustainability_score=outfit_raw.get("sustainability_score"),
            styling_tips=outfit_raw.get("styling_tips", []),
            total_estimated_price_inr=outfit_raw.get("total_estimated_price_inr"),
            llm_provider_used=llm_provider,
            image_provider_used="pending",
            shopping_provider_used="pending",
            generation_status="success",
        )
        db.add(generation)
        db.flush()

        # 4. Persist outfit items
        raw_items = outfit_raw.get("items", [])
        persisted_items: List[OutfitItem] = []
        for idx, item in enumerate(raw_items):
            colour_val = item.get("color", "")
            if isinstance(colour_val, dict):
                colour_val = colour_val.get("hex") or colour_val.get("name") or ""
            db_item = OutfitItem(
                generation_id=generation.id,
                category=item.get("category", "Item"),
                name=item.get("name", "Garment"),
                recommended_fabric=item.get("recommended_fabric") or item.get("preferred_fabric"),
                color=str(colour_val)[:50] if colour_val else None,
                estimated_price_inr=item.get("estimated_price_inr") or item.get("estimated_budget_inr"),
                sustainability_note=item.get("sustainability_note"),
                sort_order=idx,
            )
            db.add(db_item)
            persisted_items.append(db_item)

        db.flush()

        # 5. Calculate total if missing
        if not generation.total_estimated_price_inr:
            total = sum(i.estimated_price_inr or 0 for i in persisted_items)
            generation.total_estimated_price_inr = total or None

        # 6. Generate 2 to 4 outfit image variations
        items_for_image = [
            {
                "category": i.category,
                "name": i.name,
                "recommended_fabric": i.recommended_fabric,
                "color": i.color,
                "estimated_price_inr": i.estimated_price_inr,
            }
            for i in persisted_items
        ]

        img_service = get_outfit_image_service()
        primary_image_info, variations, image_provider = img_service.generate_variations(
            scenario=generation.scenario,
            outfit_name=generation.outfit_name or "Eco Outfit",
            items=items_for_image,
            color_palette=generation.color_palette or [],
            gender=generation.gender_preference,
            style=generation.style,
            season=generation.weather_season,
            variation_count=settings.OUTFIT_VARIATION_COUNT,
        )
        generation.image_provider_used = image_provider

        # Persist primary image record
        db_image = GeneratedOutfitImage(
            generation_id=generation.id,
            prompt=primary_image_info.prompt or f"AI outfit visualization for: {request.scenario}",
            image_url=primary_image_info.url or "",
            generation_mode=image_provider,
            label=IMAGE_DISCLAIMER,
        )
        db.add(db_image)
        db.flush()

        # 7. Search shopping products & generate verified Indian retailer links
        shopping_service = get_shopping_search_service()
        shopping_results, retailer_search_links, shopping_provider = shopping_service.search(
            items=items_for_image,
            gender=generation.gender_preference,
            style=generation.style,
            occasion=generation.occasion,
            budget_inr=generation.budget_inr,
            location=generation.location or "India",
            limit=settings.OUTFIT_SEARCH_RESULT_LIMIT,
        )
        generation.shopping_provider_used = shopping_provider

        shopping_search = ShoppingSearch(
            generation_id=generation.id,
            query_context={
                "scenario": request.scenario,
                "style": request.style,
                "budget_inr": request.budget_inr,
                "location": request.location,
            },
            provider_used=shopping_provider,
            search_status="success" if shopping_results else "no_results",
            total_matches=len(shopping_results),
        )
        db.add(shopping_search)
        db.flush()

        persisted_matches: List[ShoppingMatch] = []
        for prod in shopping_results:
            if not is_safe_url(prod.product_url):
                continue
            db_match = ShoppingMatch(
                search_id=shopping_search.id,
                category=prod.category,
                title=prod.title,
                brand=prod.brand or prod.retailer,
                price=prod.price_inr or prod.price,
                currency=prod.currency,
                product_url=prod.product_url,
                image_url=prod.image_url,
                fabric_details=prod.fabric_details,
                available_sizes=prod.available_sizes or [],
                match_score=prod.match_score,
                source_type=prod.source_type,
                sustainability_label=prod.sustainability_label,
            )
            db.add(db_match)
            persisted_matches.append(db_match)

        db.commit()
        db.refresh(generation)

        # 8. Build response
        outfit_schema = OutfitSchema(
            name=generation.outfit_name,
            outfit_name=generation.outfit_name or "Eco Outfit",
            occasion=generation.occasion,
            description=generation.description or "",
            items=[
                OutfitItemSchema(
                    id=it.id,
                    category=it.category,
                    name=it.name,
                    search_query=f"{generation.gender_preference or ''} {it.color or ''} {it.name}".strip(),
                    preferred_fabric=it.recommended_fabric,
                    recommended_fabric=it.recommended_fabric,
                    color=it.color,
                    estimated_budget_inr=it.estimated_price_inr,
                    estimated_price_inr=it.estimated_price_inr,
                    sustainability_note=it.sustainability_note,
                )
                for it in persisted_items
            ],
            color_palette=generation.color_palette or [],
            recommended_fabrics=generation.recommended_fabrics or [],
            sustainability_summary=generation.sustainability_summary,
            sustainability_score=generation.sustainability_score,
            styling_tips=generation.styling_tips or [],
            total_estimated_price_inr=generation.total_estimated_price_inr,
        )

        is_mock = llm_provider == "mock"

        return OutfitGenerateResponse(
            generation_id=generation.id,
            outfit=outfit_schema,
            generated_image=primary_image_info,
            generated_images=variations,
            generated_image_url=primary_image_info.url,
            generated_image_id=db_image.id,
            image_label=IMAGE_DISCLAIMER,
            shopping_results=shopping_results,
            shopping_matches=shopping_results,
            retailer_search_links=retailer_search_links,
            provider_info={
                "llm": llm_provider,
                "image": image_provider,
                "shopping": shopping_provider,
            },
            disclaimer=SHOPPING_DISCLAIMER,
            store_verification_notice=STORE_VERIFICATION_NOTICE,
            is_mock_mode=is_mock,
        )

    def get_generation(self, generation_id: int, db: Session) -> Optional[OutfitGenerateResponse]:
        """Retrieve a past generation from DB."""
        gen = db.query(OutfitGeneration).filter(OutfitGeneration.id == generation_id).first()
        if not gen:
            return None

        items = (
            db.query(OutfitItem)
            .filter(OutfitItem.generation_id == generation_id)
            .order_by(OutfitItem.sort_order)
            .all()
        )
        img = (
            db.query(GeneratedOutfitImage)
            .filter(GeneratedOutfitImage.generation_id == generation_id)
            .order_by(GeneratedOutfitImage.id.desc())
            .first()
        )

        items_for_service = [
            {
                "category": i.category,
                "name": i.name,
                "recommended_fabric": i.recommended_fabric,
                "color": i.color,
                "estimated_price_inr": i.estimated_price_inr,
            }
            for i in items
        ]

        img_service = get_outfit_image_service()
        primary_image_info, variations, _ = img_service.generate_variations(
            scenario=gen.scenario,
            outfit_name=gen.outfit_name or "Eco Outfit",
            items=items_for_service,
            color_palette=gen.color_palette or [],
            gender=gen.gender_preference,
            style=gen.style,
            season=gen.weather_season,
        )
        if img:
            primary_image_info.url = img.image_url

        shopping_service = get_shopping_search_service()
        shopping_results, retailer_search_links, _ = shopping_service.search(
            items=items_for_service,
            gender=gen.gender_preference,
            style=gen.style,
            occasion=gen.occasion,
            budget_inr=gen.budget_inr,
            location=gen.location or "India",
        )

        outfit_schema = OutfitSchema(
            name=gen.outfit_name,
            outfit_name=gen.outfit_name or "Eco Outfit",
            occasion=gen.occasion,
            description=gen.description or "",
            items=[
                OutfitItemSchema(
                    id=it.id,
                    category=it.category,
                    name=it.name,
                    search_query=f"{gen.gender_preference or ''} {it.color or ''} {it.name}".strip(),
                    preferred_fabric=it.recommended_fabric,
                    recommended_fabric=it.recommended_fabric,
                    color=it.color,
                    estimated_budget_inr=it.estimated_price_inr,
                    estimated_price_inr=it.estimated_price_inr,
                    sustainability_note=it.sustainability_note,
                )
                for it in items
            ],
            color_palette=gen.color_palette or [],
            recommended_fabrics=gen.recommended_fabrics or [],
            sustainability_summary=gen.sustainability_summary,
            sustainability_score=gen.sustainability_score,
            styling_tips=gen.styling_tips or [],
            total_estimated_price_inr=gen.total_estimated_price_inr,
        )

        return OutfitGenerateResponse(
            generation_id=gen.id,
            outfit=outfit_schema,
            generated_image=primary_image_info,
            generated_images=variations,
            generated_image_url=img.image_url if img else primary_image_info.url,
            generated_image_id=img.id if img else None,
            image_label=IMAGE_DISCLAIMER,
            shopping_results=shopping_results,
            shopping_matches=shopping_results,
            retailer_search_links=retailer_search_links,
            provider_info={
                "llm": gen.llm_provider_used or "mock",
                "image": gen.image_provider_used or "mock",
                "shopping": gen.shopping_provider_used or "mock",
            },
            disclaimer=SHOPPING_DISCLAIMER,
            store_verification_notice=STORE_VERIFICATION_NOTICE,
            is_mock_mode=gen.llm_provider_used == "mock",
        )

    def regenerate_image(
        self,
        generation_id: int,
        db: Session,
        variation_index: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """Regenerate a specific concept variation."""
        gen = db.query(OutfitGeneration).filter(OutfitGeneration.id == generation_id).first()
        if not gen:
            return None

        items = db.query(OutfitItem).filter(OutfitItem.generation_id == generation_id).all()
        items_for_image = [
            {
                "category": i.category,
                "name": i.name,
                "recommended_fabric": i.recommended_fabric,
                "color": i.color,
                "estimated_price_inr": i.estimated_price_inr,
            }
            for i in items
        ]

        img_service = get_outfit_image_service()
        variation = img_service.regenerate_single_variation(
            scenario=gen.scenario,
            outfit_name=gen.outfit_name or "Eco Outfit",
            items=items_for_image,
            color_palette=gen.color_palette or [],
            gender=gen.gender_preference,
            style=gen.style,
            season=gen.weather_season,
            variation_index=variation_index,
        )

        db_image = GeneratedOutfitImage(
            generation_id=generation_id,
            prompt=variation.prompt or f"Regenerated variation {variation_index} for: {gen.scenario}",
            image_url=variation.image_url,
            generation_mode=variation.status,
            label=IMAGE_DISCLAIMER,
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return {
            "image_url": variation.image_url,
            "image_id": db_image.id,
            "variation_index": variation.variation_index,
            "variation_title": variation.variation_title,
            "status": variation.status,
            "label": IMAGE_DISCLAIMER,
            "prompt": variation.prompt,
        }

    def get_history(self, user_id: int, db: Session, limit: int = 20) -> List[OutfitHistoryItem]:
        """Return user's outfit generation history."""
        generations = (
            db.query(OutfitGeneration)
            .filter(OutfitGeneration.user_id == user_id)
            .order_by(OutfitGeneration.created_at.desc())
            .limit(limit)
            .all()
        )
        results = []
        for gen in generations:
            img = (
                db.query(GeneratedOutfitImage)
                .filter(GeneratedOutfitImage.generation_id == gen.id)
                .order_by(GeneratedOutfitImage.id.desc())
                .first()
            )
            results.append(
                OutfitHistoryItem(
                    generation_id=gen.id,
                    outfit_name=gen.outfit_name,
                    scenario=gen.scenario,
                    style=gen.style,
                    gender_preference=gen.gender_preference,
                    budget_inr=gen.budget_inr,
                    total_estimated_price_inr=gen.total_estimated_price_inr,
                    generated_image_url=img.image_url if img else None,
                    sustainability_score=gen.sustainability_score,
                    created_at=gen.created_at,
                )
            )
        return results

    def save_outfit(
        self,
        generation_id: int,
        user_id: int,
        db: Session,
        project_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> SavedOutfitResponse:
        existing = (
            db.query(SavedOutfit)
            .filter(SavedOutfit.generation_id == generation_id, SavedOutfit.user_id == user_id)
            .first()
        )
        if existing:
            return SavedOutfitResponse(
                id=existing.id,
                user_id=existing.user_id,
                generation_id=existing.generation_id,
                project_id=existing.project_id,
                notes=existing.notes,
                saved_at=existing.saved_at,
            )
        saved = SavedOutfit(
            user_id=user_id,
            generation_id=generation_id,
            project_id=project_id,
            notes=notes,
        )
        db.add(saved)
        db.commit()
        db.refresh(saved)
        return SavedOutfitResponse(
            id=saved.id,
            user_id=saved.user_id,
            generation_id=saved.generation_id,
            project_id=saved.project_id,
            notes=saved.notes,
            saved_at=saved.saved_at,
        )

    def get_saved_outfits(self, user_id: int, db: Session) -> List[OutfitHistoryItem]:
        saved = (
            db.query(SavedOutfit)
            .filter(SavedOutfit.user_id == user_id)
            .order_by(SavedOutfit.saved_at.desc())
            .all()
        )
        results = []
        for s in saved:
            gen = db.query(OutfitGeneration).filter(OutfitGeneration.id == s.generation_id).first()
            if not gen:
                continue
            img = (
                db.query(GeneratedOutfitImage)
                .filter(GeneratedOutfitImage.generation_id == gen.id)
                .order_by(GeneratedOutfitImage.id.desc())
                .first()
            )
            results.append(
                OutfitHistoryItem(
                    generation_id=gen.id,
                    outfit_name=gen.outfit_name,
                    scenario=gen.scenario,
                    style=gen.style,
                    gender_preference=gen.gender_preference,
                    budget_inr=gen.budget_inr,
                    total_estimated_price_inr=gen.total_estimated_price_inr,
                    generated_image_url=img.image_url if img else None,
                    sustainability_score=gen.sustainability_score,
                    created_at=gen.created_at,
                )
            )
        return results

    def unsave_outfit(self, saved_id: int, user_id: int, db: Session) -> bool:
        saved = db.query(SavedOutfit).filter(
            SavedOutfit.id == saved_id, SavedOutfit.user_id == user_id
        ).first()
        if not saved:
            return False
        db.delete(saved)
        db.commit()
        return True


# Singleton
_service_instance: Optional[OutfitGeneratorService] = None

def get_outfit_generator_service() -> OutfitGeneratorService:
    global _service_instance
    if _service_instance is None:
        _service_instance = OutfitGeneratorService()
    return _service_instance
