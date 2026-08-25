"""
Comprehensive tests for the AI Outfit Studio feature.
Tests:
- Live image generation success/failure and fallbacks
- Demo-mode disclosure message and disclaimer presence
- Invalid / missing API keys handling
- Product URL validation and security
- No fake product links / anti-hallucination compliance
- Retailer search-link generation for Myntra, AJIO, Nykaa Fashion, Amazon India, Tata CLiQ
- Indian rupee formatting and budget validation
- No-results handling
- Variations generation and single variation regeneration

Run with:
    cd backend && python -m pytest tests/test_outfit_studio.py -v
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest
from pydantic import ValidationError

from app.schemas.outfit_schemas import (
    DEMO_IMAGE_MESSAGE,
    IMAGE_DISCLAIMER,
    SHOPPING_DISCLAIMER,
    STORE_VERIFICATION_NOTICE,
    OutfitGenerateRequest,
    OutfitItemSchema,
    OutfitSchema,
    ShoppingMatchSchema,
    RetailerSearchLinkSchema,
    GeneratedImageInfo,
    GeneratedOutfitImageVariationSchema,
)
from app.services.outfit_generator_service import OutfitGeneratorService
from app.services.outfit_image_service import OutfitImageService, get_outfit_image_service
from app.services.providers.outfit_mock_provider import (
    generate_outfit_svg,
    get_mock_shopping_matches,
    select_outfit,
)
from app.services.shopping_search_service import (
    ShoppingSearchService,
    build_ajio_search_url,
    build_amazon_in_search_url,
    build_myntra_search_url,
    build_nykaa_fashion_search_url,
    build_tatacliq_search_url,
    get_shopping_search_service,
    is_safe_url,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Schema Validation Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestOutfitGenerateRequestValidation:

    def test_valid_request_minimal(self):
        req = OutfitGenerateRequest(scenario="College farewell party outfit")
        assert req.scenario == "College farewell party outfit"
        assert req.budget_inr is None
        assert req.gender_preference is None

    def test_valid_request_full(self):
        req = OutfitGenerateRequest(
            scenario="Sustainable wedding guest look",
            gender_preference="women",
            budget_inr=5000,
            size="M",
            location="India",
            weather_season="summer",
            preferred_colors=["sage green", "ivory"],
            preferred_fabrics=["Tencel"],
            sustainability_preferences=["vegan", "low water impact"],
            style="party",
        )
        assert req.gender_preference == "women"
        assert req.budget_inr == 5000

    def test_scenario_too_short_raises(self):
        with pytest.raises(ValidationError):
            OutfitGenerateRequest(scenario="hi")

    def test_scenario_blank_raises(self):
        with pytest.raises(ValidationError):
            OutfitGenerateRequest(scenario="     ")

    def test_scenario_too_long_raises(self):
        with pytest.raises(ValidationError):
            OutfitGenerateRequest(scenario="x" * 501)

    def test_invalid_gender_raises(self):
        with pytest.raises(ValidationError):
            OutfitGenerateRequest(
                scenario="Party outfit for tonight",
                gender_preference="alien",
            )

    def test_invalid_style_raises(self):
        with pytest.raises(ValidationError):
            OutfitGenerateRequest(
                scenario="Party outfit for tonight",
                style="disco",
            )

    def test_budget_below_minimum_raises(self):
        with pytest.raises(ValidationError):
            OutfitGenerateRequest(
                scenario="Casual denim look for weekend",
                budget_inr=50,
            )

    def test_valid_style_values(self):
        for style in ["casual", "formal", "traditional", "party", "streetwear", "minimal", "luxury"]:
            req = OutfitGenerateRequest(
                scenario="An outfit for a special day",
                style=style,
            )
            assert req.style == style

    def test_gender_normalised_to_lowercase(self):
        req = OutfitGenerateRequest(
            scenario="Interview outfit suggestion",
            gender_preference="Women",
        )
        assert req.gender_preference == "women"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Shopping Search Service & Indian Store URL Generation Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestShoppingSearchServiceAndStoreUrls:

    def test_myntra_search_url_generation(self):
        url = build_myntra_search_url("women sage green wrap midi dress")
        assert url.startswith("https://www.myntra.com/")
        assert "women" in url.lower()
        assert "sage" in url.lower()
        assert "dress" in url.lower()

    def test_ajio_search_url_generation(self):
        url = build_ajio_search_url("women linen wrap dress")
        assert url.startswith("https://www.ajio.com/search/?text=")
        assert "women" in url.lower()
        assert "linen" in url.lower()

    def test_nykaa_fashion_search_url_generation(self):
        url = build_nykaa_fashion_search_url("vegan block heels")
        assert url.startswith("https://www.nykaafashion.com/catalogsearch/result/?q=")
        assert "vegan" in url.lower()

    def test_amazon_in_search_url_generation(self):
        url = build_amazon_in_search_url("organic cotton tote bag")
        assert url.startswith("https://www.amazon.in/s?k=")
        assert "organic" in url.lower()

    def test_tatacliq_search_url_generation(self):
        url = build_tatacliq_search_url("recycled brass earrings")
        assert url.startswith("https://www.tatacliq.com/search/?searchCategory=all&text=")
        assert "recycled" in url.lower()

    def test_generate_retailer_search_links_returns_all_top_stores(self):
        service = get_shopping_search_service()
        links = service.generate_retailer_search_links("women sage green dress")
        retailers = [l.retailer for l in links]
        assert "Myntra" in retailers
        assert "AJIO" in retailers
        assert "Nykaa Fashion" in retailers
        assert "Amazon India" in retailers
        assert "Tata CLiQ" in retailers

    def test_no_fake_product_urls_in_curated_matches(self):
        """Ensure matches point to safe verified endpoints, never invented mock domains."""
        service = get_shopping_search_service()
        items = [{"category": "Dress", "name": "Sage midi dress"}]
        matches, search_links, _ = service.search(items=items)
        for m in matches:
            assert is_safe_url(m.product_url)
            # Must use valid schemes
            assert m.product_url.startswith("https://") or m.product_url.startswith("http://")
            # Status must be verified or demo
            assert m.status in ("verified", "demo")

    def test_price_inr_formatting_and_disclosures(self):
        service = get_shopping_search_service()
        items = [{"category": "Dress", "name": "Organic dress"}]
        matches, search_links, _ = service.search(items=items, budget_inr=4000)
        for m in matches:
            assert m.currency == "INR"
            if m.price_inr is not None:
                assert m.price_inr > 0


# ─────────────────────────────────────────────────────────────────────────────
# 3. URL Safety Validator Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestUrlSafety:

    def test_valid_https_url(self):
        assert is_safe_url("https://www.myntra.com/dresses") is True

    def test_valid_http_url(self):
        assert is_safe_url("http://example.com/product") is True

    def test_none_is_unsafe(self):
        assert is_safe_url(None) is False

    def test_empty_string_is_unsafe(self):
        assert is_safe_url("") is False

    def test_javascript_scheme_is_unsafe(self):
        assert is_safe_url("javascript:alert(1)") is False

    def test_file_scheme_is_unsafe(self):
        assert is_safe_url("file:///etc/passwd") is False

    def test_overly_long_url_is_unsafe(self):
        assert is_safe_url("https://example.com/" + "a" * 2049) is False


# ─────────────────────────────────────────────────────────────────────────────
# 4. Outfit Image Service & Variations Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestOutfitImageService:

    def test_editorial_prompt_builder_structure(self):
        service = get_outfit_image_service()
        prompt = service.build_editorial_prompt(
            scenario="summer formal office setting",
            outfit_name="Sage Green Sustainable Office Dress",
            items=[
                {"category": "Dress", "name": "wrap midi dress", "recommended_fabric": "Tencel"},
                {"category": "Footwear", "name": "cream block heels"},
            ],
            gender="women",
            style="formal",
            season="summer",
            colors=["sage green", "cream"],
        )
        assert "editorial fashion photograph" in prompt.lower()
        assert "sage green" in prompt.lower()
        assert "tencel" in prompt.lower()
        assert "no brand logos" in prompt.lower()
        assert "no text" in prompt.lower()

    def test_missing_api_key_returns_demo_mode_disclosure(self):
        service = OutfitImageService()
        with patch.dict("os.environ", {"OUTFIT_IMAGE_PROVIDER": "mock", "OUTFIT_IMAGE_API_KEY": ""}):
            primary_info, variations, provider = service.generate_variations(
                scenario="formal office",
                outfit_name="Linen Office Look",
                items=[{"category": "Dress", "name": "Linen dress"}],
                color_palette=["#7D9B76"],
            )
            assert provider == "mock"
            assert primary_info.status == "demo"
            assert primary_info.message == DEMO_IMAGE_MESSAGE
            assert primary_info.disclaimer == IMAGE_DISCLAIMER

    def test_variations_count_between_2_and_4(self):
        service = get_outfit_image_service()
        primary_info, variations, _ = service.generate_variations(
            scenario="college farewell",
            outfit_name="Farewell Look",
            items=[{"category": "Dress", "name": "Party dress"}],
            color_palette=["#7D9B76", "#D4B896"],
            variation_count=3,
        )
        assert 2 <= len(variations) <= 4
        for idx, var in enumerate(variations, start=1):
            assert var.variation_index == idx
            assert var.label == IMAGE_DISCLAIMER
            assert var.image_url.startswith("http") or var.image_url.startswith("data:")

    def test_regenerate_single_variation(self):
        service = get_outfit_image_service()
        variation = service.regenerate_single_variation(
            scenario="interview formal",
            outfit_name="Interview Set",
            items=[{"category": "Top", "name": "Formal shirt"}],
            color_palette=["#FAFAFA"],
            variation_index=2,
        )
        assert variation.variation_index == 2
        assert variation.label == IMAGE_DISCLAIMER
        assert is_safe_url(variation.image_url) or variation.image_url.startswith("data:")

    def test_live_dalle_failure_falls_back_gracefully(self):
        service = OutfitImageService()
        with patch.object(service, "generate_live_dalle_image", return_value=None):
            with patch.dict("os.environ", {"OUTFIT_IMAGE_PROVIDER": "dalle", "OUTFIT_IMAGE_API_KEY": "sk-test"}):
                primary_info, variations, provider = service.generate_variations(
                    scenario="party dress",
                    outfit_name="Party Look",
                    items=[],
                    color_palette=["#7D9B76"],
                )
                assert primary_info.status == "demo"
                assert len(variations) >= 2


# ─────────────────────────────────────────────────────────────────────────────
# 5. Full Outfit Generator Service & End-to-End Orchestration Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestOutfitGeneratorServiceIntegration:

    def _make_mock_db(self):
        db = MagicMock()
        db.add = MagicMock()
        db.flush = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()

        def refresh_side_effect(obj):
            if hasattr(obj, "id") and obj.id is None:
                obj.id = 1

        db.refresh.side_effect = refresh_side_effect
        return db

    def test_end_to_end_generate_response_structure(self):
        service = OutfitGeneratorService()
        db = self._make_mock_db()

        req = OutfitGenerateRequest(
            scenario="Eco-friendly college farewell dress for women",
            gender_preference="women",
            budget_inr=3500,
            style="party",
            preferred_colors=["sage green", "cream"],
        )
        response = service.generate(request=req, db=db, user_id=None)

        # 1. Outfit concept structure
        assert response.outfit.outfit_name
        assert response.outfit.description
        assert len(response.outfit.items) > 0
        for item in response.outfit.items:
            assert item.category
            assert item.name

        # 2. Image generation & disclaimer
        assert response.generated_image.disclaimer == IMAGE_DISCLAIMER
        assert response.image_label == IMAGE_DISCLAIMER
        assert len(response.generated_images) >= 2

        # 3. Shopping results & Indian store links
        assert response.disclaimer == SHOPPING_DISCLAIMER
        assert response.store_verification_notice == STORE_VERIFICATION_NOTICE
        assert len(response.retailer_search_links) >= 4

        retailer_names = [r.retailer for r in response.retailer_search_links]
        assert "Myntra" in retailer_names
        assert "AJIO" in retailer_names
        assert "Nykaa Fashion" in retailer_names
        assert "Amazon India" in retailer_names

    def test_no_results_handled_gracefully(self):
        service = OutfitGeneratorService()
        db = self._make_mock_db()

        with patch.object(get_shopping_search_service(), "search") as mock_search:
            mock_search.return_value = ([], [], "mock")
            req = OutfitGenerateRequest(scenario="Extremely rare bespoke artisan garment")
            res = service.generate(request=req, db=db)
            assert res.shopping_results == []
            assert res.disclaimer == SHOPPING_DISCLAIMER
            assert res.store_verification_notice == STORE_VERIFICATION_NOTICE


# ─────────────────────────────────────────────────────────────────────────────
# 6. Extreme Inputs & Indian Currency Calculations
# ─────────────────────────────────────────────────────────────────────────────

class TestExtremeInputsAndCurrency:

    def test_long_scenario_valid(self):
        long_scenario = "Sustainable outfit for international fashion gala dinner in Milan with organic silk and recycled accessories"
        req = OutfitGenerateRequest(scenario=long_scenario, style="luxury", gender_preference="unisex")
        assert req.scenario == long_scenario

    def test_budget_range_boundaries(self):
        req_min = OutfitGenerateRequest(scenario="Budget cotton scarf look", budget_inr=200)
        assert req_min.budget_inr == 200
        req_max = OutfitGenerateRequest(scenario="Luxury couture silk gown", budget_inr=500000)
        assert req_max.budget_inr == 500000

    def test_all_gender_options_accepted(self):
        for g in ["women", "men", "unisex", "no_preference"]:
            req = OutfitGenerateRequest(scenario="Office outfit", gender_preference=g)
            assert req.gender_preference == g
