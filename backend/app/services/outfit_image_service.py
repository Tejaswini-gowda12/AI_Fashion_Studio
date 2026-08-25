"""
Outfit Image Service
====================
Handles generation of realistic fashion concept visualizations and multi-variation sets:
1. Builds rich editorial fashion prompts following professional photography standards.
2. Coordinates with live image providers (OpenAI DALL-E 3, Gemini, etc.) when configured.
3. Automatically produces 2 to 4 distinct variations (e.g., Full-Body Editorial, Drape Detail, Styling Set).
4. Handles loading, timeouts, API failures, and clean fallback states.
5. In demo mode or when API key is missing, provides high-quality realistic concept images
   and explicitly discloses:
   "Live outfit-image generation is not configured. Showing a demo concept."
6. Strictly attaches the mandatory disclosure label to every image:
   "AI-generated style concept — not an exact purchasable product."
"""
from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.schemas.outfit_schemas import (
    DEMO_IMAGE_MESSAGE,
    IMAGE_DISCLAIMER,
    GeneratedImageInfo,
    GeneratedOutfitImageVariationSchema,
)
from app.services.providers.outfit_mock_provider import generate_outfit_svg

logger = logging.getLogger(__name__)

# High-resolution curated editorial fashion photo references for realistic demo rendering
_REALISTIC_CONCEPT_PHOTOS = {
    "men_formal": [
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1200&auto=format&fit=crop&q=85", # Sharp tailored suit
        "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=1200&auto=format&fit=crop&q=85", # Navy suit & dress shirt
        "https://images.unsplash.com/photo-1598808503746-f34c53b9323e?w=1200&auto=format&fit=crop&q=85", # Formal blazer & trousers
        "https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=1200&auto=format&fit=crop&q=85", # Business formal look
    ],
    "men_traditional": [
        "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=1200&auto=format&fit=crop&q=85", # Men ethnic kurta & nehru jacket
        "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?w=1200&auto=format&fit=crop&q=85", # Festive royal kurta
        "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=1200&auto=format&fit=crop&q=85", # Handspun kurta set
    ],
    "men_casual": [
        "https://images.unsplash.com/photo-1516826957135-700dedea698c?w=1200&auto=format&fit=crop&q=85", # Denim & casual shirt
        "https://images.unsplash.com/photo-1520975954732-35dd22299614?w=1200&auto=format&fit=crop&q=85", # Weekend look
        "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=1200&auto=format&fit=crop&q=85", # Street casual
    ],
    "women_dress": [
        "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=1200&auto=format&fit=crop&q=85", # Sage green wrap midi dress
        "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=1200&auto=format&fit=crop&q=85", # Linen wrap dress
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1200&auto=format&fit=crop&q=85", # Elegant party dress
        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=1200&auto=format&fit=crop&q=85", # Flowing midi silhouette
    ],
    "women_formal": [
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=1200&auto=format&fit=crop&q=85", # Women linen office co-ord
        "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=1200&auto=format&fit=crop&q=85", # Tailored blazer look
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=1200&auto=format&fit=crop&q=85", # Professional boardroom
    ],
    "women_traditional": [
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=1200&auto=format&fit=crop&q=85", # Handloom Anarkali
        "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=1200&auto=format&fit=crop&q=85", # Festive ethnic wear
        "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?w=1200&auto=format&fit=crop&q=85", # Chanderi ensemble
    ],
    "general": [
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1445205170230-053b83016050?w=1200&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=1200&auto=format&fit=crop&q=85",
    ]
}


class OutfitImageService:

    def build_editorial_prompt(
        self,
        scenario: str,
        outfit_name: str,
        items: List[Dict[str, Any]],
        gender: Optional[str] = None,
        style: Optional[str] = None,
        season: Optional[str] = None,
        colors: Optional[List[str]] = None,
        variation_type: str = "full_body",
    ) -> str:
        """
        Constructs a detailed prompt adhering to high-fashion editorial standards.
        """
        g = (gender or "").lower()
        text = f"{scenario} {outfit_name}".lower()

        has_men_token = bool(re.search(r"\b(men|mens|men's|man|male|gentleman|boy)\b", text))
        has_women_token = bool(re.search(r"\b(women|womens|women's|woman|female|lady|ladies|girl)\b", text))

        if g == "men" or (has_men_token and not has_women_token):
            subject = "a stylish man"
        elif g == "women" or (has_women_token and not has_men_token):
            subject = "a woman"
        elif g == "unisex":
            subject = "a fashion model"
        else:
            subject = "a model"

        color_phrase = ", ".join(colors[:3]) if colors else "earthy natural tones"
        season_phrase = f"{season} " if season else ""
        style_phrase = f"{style} " if style else ""

        item_phrases: List[str] = []
        primary_fabric = ""
        for it in items[:4]:
            nm = it.get("name", "")
            fab = it.get("recommended_fabric") or it.get("preferred_fabric") or ""
            if not primary_fabric and fab:
                primary_fabric = fab.split("/")[0]
            item_phrases.append(f"{nm} in {fab}" if fab else nm)

        garments_desc = ", ".join(item_phrases) if item_phrases else outfit_name
        fabric_text = f"sustainable {primary_fabric} " if primary_fabric else "sustainable organic textile "

        if variation_type == "drape_detail":
            view_angle = (
                f"Close-up fashion editorial shot showing fine drape, seams and natural textile weave of {outfit_name}, "
                f"intricate tailoring details, soft natural folds, elegant silhouette detail"
            )
        elif variation_type == "styling_angle":
            view_angle = (
                f"Three-quarter angle lookbook fashion photoshoot of {subject} wearing {outfit_name}, "
                f"styled with coordinated eco accessories and formal shoes, confident natural pose"
            )
        else:
            view_angle = (
                f"Full-body editorial fashion photograph of {subject} wearing {fabric_text}{garments_desc} "
                f"for a {season_phrase}{style_phrase}{scenario}"
            )

        prompt = (
            f"{view_angle}, palette of {color_phrase}, elegant modest silhouette, "
            f"natural studio lighting, realistic fabric texture, clean professional fashion catalogue image, "
            f"photorealistic 8k quality, no brand logos, no text, no watermarks."
        )
        return prompt

    def generate_live_dalle_image(
        self,
        prompt: str,
        api_key: str,
    ) -> Optional[str]:
        """Call OpenAI DALL-E with the editorial prompt."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            if response.data and len(response.data) > 0:
                return response.data[0].url
        except Exception as e:
            logger.warning("Live DALL-E image generation failed: %s", e)
        return None

    def generate_live_pollinations_image(
        self,
        prompt: str,
        seed: Optional[int] = None,
    ) -> str:
        """
        Free real-time photorealistic AI fashion generation using Flux / SDXL.
        Generates custom high-resolution style visualizations without API quota limits.
        """
        import urllib.parse
        clean_prompt = prompt.replace("\n", " ").strip()
        encoded = urllib.parse.quote(clean_prompt[:400])
        seed_str = f"&seed={seed}" if seed else ""
        return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&enhance=true&model=flux{seed_str}"

    def get_demo_concept_image(
        self,
        scenario: str,
        outfit_name: str,
        items: List[Dict[str, Any]],
        color_palette: List[str],
        style: Optional[str] = None,
        gender: Optional[str] = None,
        variation_index: int = 1,
    ) -> str:
        """
        Returns a high-quality realistic concept photo strictly respecting gender & style.
        """
        text = f"{scenario} {outfit_name} {style or ''}".lower()
        g_pref = (gender or "").lower()

        has_men_token = bool(re.search(r"\b(men|mens|men's|man|male|gentleman|boy)\b", text))
        has_women_token = bool(re.search(r"\b(women|womens|women's|woman|female|lady|ladies|girl)\b", text))

        is_men = g_pref == "men" or (has_men_token and not has_women_token)
        is_women = g_pref == "women" or (has_women_token and not has_men_token)

        if is_men:
            if any(k in text for k in ["traditional", "ethnic", "kurta", "bundi", "sherwani", "wedding", "festive"]):
                photos = _REALISTIC_CONCEPT_PHOTOS["men_traditional"]
            elif any(k in text for k in ["casual", "denim", "weekend", "street", "trip", "travel"]):
                photos = _REALISTIC_CONCEPT_PHOTOS["men_casual"]
            else:
                photos = _REALISTIC_CONCEPT_PHOTOS["men_formal"]
        elif is_women:
            if any(k in text for k in ["traditional", "anarkali", "ethnic", "saree", "dupatta", "wedding", "festive"]):
                photos = _REALISTIC_CONCEPT_PHOTOS["women_traditional"]
            elif any(k in text for k in ["office", "blazer", "trouser", "formal", "work", "meeting"]) and "dress" not in text:
                photos = _REALISTIC_CONCEPT_PHOTOS["women_formal"]
            else:
                photos = _REALISTIC_CONCEPT_PHOTOS["women_dress"]
        else:
            if any(k in text for k in ["suit", "blazer", "formal", "office"]):
                photos = _REALISTIC_CONCEPT_PHOTOS["men_formal"]
            elif any(k in text for k in ["dress", "gown", "midi"]):
                photos = _REALISTIC_CONCEPT_PHOTOS["women_dress"]
            else:
                photos = _REALISTIC_CONCEPT_PHOTOS["general"]

        idx = (variation_index - 1) % len(photos)
        return photos[idx]

    def generate_variations(
        self,
        scenario: str,
        outfit_name: str,
        items: List[Dict[str, Any]],
        color_palette: List[str],
        gender: Optional[str] = None,
        style: Optional[str] = None,
        season: Optional[str] = None,
        variation_count: int = 3,
    ) -> Tuple[GeneratedImageInfo, List[GeneratedOutfitImageVariationSchema], str]:
        """
        Generate 2 to 4 outfit image variations.
        """
        provider = os.getenv("OUTFIT_IMAGE_PROVIDER", settings.OUTFIT_IMAGE_PROVIDER).lower()
        api_key = (
            os.getenv("OUTFIT_IMAGE_API_KEY")
            or settings.OUTFIT_IMAGE_API_KEY
            or os.getenv("OPENAI_API_KEY")
            or settings.OPENAI_API_KEY
        )

        variation_types = [
            ("full_body", "Editorial Full-Body Look"),
            ("drape_detail", "Textile & Drape Detail"),
            ("styling_angle", "Lookbook Styling Angle"),
            ("palette_focus", "Alternative Silhouette"),
        ]

        count = max(2, min(4, variation_count or settings.OUTFIT_VARIATION_COUNT))
        variations: List[GeneratedOutfitImageVariationSchema] = []

        is_live_configured = (provider in ("dalle", "openai") and bool(api_key and not api_key.startswith("sk-proj-placeholder")))

        if is_live_configured:
            primary_prompt = self.build_editorial_prompt(
                scenario=scenario,
                outfit_name=outfit_name,
                items=items,
                gender=gender,
                style=style,
                season=season,
                colors=color_palette,
                variation_type="full_body",
            )
            live_url = self.generate_live_dalle_image(primary_prompt, api_key)
            if live_url:
                variations.append(
                    GeneratedOutfitImageVariationSchema(
                        variation_index=1,
                        variation_title="Editorial Full-Body Look",
                        image_url=live_url,
                        status="generated",
                        label=IMAGE_DISCLAIMER,
                        prompt=primary_prompt,
                    )
                )
                for idx in range(2, count + 1):
                    vtype, vtitle = variation_types[idx - 1]
                    fallback_url = self.get_demo_concept_image(
                        scenario=scenario,
                        outfit_name=outfit_name,
                        items=items,
                        color_palette=color_palette,
                        style=style,
                        gender=gender,
                        variation_index=idx,
                    )
                    vprompt = self.build_editorial_prompt(
                        scenario=scenario,
                        outfit_name=outfit_name,
                        items=items,
                        gender=gender,
                        style=style,
                        season=season,
                        colors=color_palette,
                        variation_type=vtype,
                    )
                    variations.append(
                        GeneratedOutfitImageVariationSchema(
                            variation_index=idx,
                            variation_title=vtitle,
                            image_url=fallback_url,
                            status="demo",
                            label=IMAGE_DISCLAIMER,
                            prompt=vprompt,
                        )
                    )

                primary_info = GeneratedImageInfo(
                    url=live_url,
                    status="generated",
                    disclaimer=IMAGE_DISCLAIMER,
                    message=None,
                    prompt=primary_prompt,
                )
                return primary_info, variations, "dalle"

        if provider in ("pollinations", "flux", "ai", "free_ai"):
            primary_prompt = self.build_editorial_prompt(
                scenario=scenario,
                outfit_name=outfit_name,
                items=items,
                gender=gender,
                style=style,
                season=season,
                colors=color_palette,
                variation_type="full_body",
            )
            live_url = self.generate_live_pollinations_image(primary_prompt, seed=101)
            variations.append(
                GeneratedOutfitImageVariationSchema(
                    variation_index=1,
                    variation_title="Editorial Full-Body Look",
                    image_url=live_url,
                    status="generated",
                    label=IMAGE_DISCLAIMER,
                    prompt=primary_prompt,
                )
            )
            for idx in range(2, count + 1):
                vtype, vtitle = variation_types[idx - 1]
                vprompt = self.build_editorial_prompt(
                    scenario=scenario,
                    outfit_name=outfit_name,
                    items=items,
                    gender=gender,
                    style=style,
                    season=season,
                    colors=color_palette,
                    variation_type=vtype,
                )
                v_url = self.generate_live_pollinations_image(vprompt, seed=idx * 107)
                variations.append(
                    GeneratedOutfitImageVariationSchema(
                        variation_index=idx,
                        variation_title=vtitle,
                        image_url=v_url,
                        status="generated",
                        label=IMAGE_DISCLAIMER,
                        prompt=vprompt,
                    )
                )
            primary_info = GeneratedImageInfo(
                url=live_url,
                status="generated",
                disclaimer=IMAGE_DISCLAIMER,
                message=None,
                prompt=primary_prompt,
            )
            return primary_info, variations, "pollinations-flux"

        # Fallback / Demo mode
        for idx in range(1, count + 1):
            vtype, vtitle = variation_types[idx - 1]
            demo_url = self.get_demo_concept_image(
                scenario=scenario,
                outfit_name=outfit_name,
                items=items,
                color_palette=color_palette,
                style=style,
                gender=gender,
                variation_index=idx,
            )
            prompt = self.build_editorial_prompt(
                scenario=scenario,
                outfit_name=outfit_name,
                items=items,
                gender=gender,
                style=style,
                season=season,
                colors=color_palette,
                variation_type=vtype,
            )
            variations.append(
                GeneratedOutfitImageVariationSchema(
                    variation_index=idx,
                    variation_title=vtitle,
                    image_url=demo_url,
                    status="demo",
                    label=IMAGE_DISCLAIMER,
                    prompt=prompt,
                )
            )

        primary_info = GeneratedImageInfo(
            url=variations[0].image_url if variations else None,
            status="demo",
            disclaimer=IMAGE_DISCLAIMER,
            message=DEMO_IMAGE_MESSAGE,
            prompt=variations[0].prompt if variations else None,
        )
        return primary_info, variations, "mock"

    def regenerate_single_variation(
        self,
        scenario: str,
        outfit_name: str,
        items: List[Dict[str, Any]],
        color_palette: List[str],
        gender: Optional[str] = None,
        style: Optional[str] = None,
        season: Optional[str] = None,
        variation_index: int = 1,
    ) -> GeneratedOutfitImageVariationSchema:
        """Regenerate a specific variation."""
        provider = os.getenv("OUTFIT_IMAGE_PROVIDER", settings.OUTFIT_IMAGE_PROVIDER).lower()
        api_key = (
            os.getenv("OUTFIT_IMAGE_API_KEY")
            or settings.OUTFIT_IMAGE_API_KEY
            or os.getenv("OPENAI_API_KEY")
            or settings.OPENAI_API_KEY
        )

        vtypes = ["full_body", "drape_detail", "styling_angle", "palette_focus"]
        titles = [
            "Editorial Full-Body Look",
            "Textile & Drape Detail",
            "Lookbook Styling Angle",
            "Alternative Silhouette",
        ]
        vidx = max(1, min(4, variation_index))
        vtype = vtypes[vidx - 1]
        title = titles[vidx - 1]

        prompt = self.build_editorial_prompt(
            scenario=scenario,
            outfit_name=outfit_name,
            items=items,
            gender=gender,
            style=style,
            season=season,
            colors=color_palette,
            variation_type=vtype,
        )

        if provider in ("pollinations", "flux", "ai", "free_ai"):
            live_url = self.generate_live_pollinations_image(prompt, seed=vidx * 211 + 37)
            return GeneratedOutfitImageVariationSchema(
                variation_index=vidx,
                variation_title=title,
                image_url=live_url,
                status="generated",
                label=IMAGE_DISCLAIMER,
                prompt=prompt,
            )

        if provider in ("dalle", "openai") and api_key and not api_key.startswith("sk-proj-placeholder"):
            live_url = self.generate_live_dalle_image(prompt, api_key)
            if live_url:
                return GeneratedOutfitImageVariationSchema(
                    variation_index=vidx,
                    variation_title=title,
                    image_url=live_url,
                    status="generated",
                    label=IMAGE_DISCLAIMER,
                    prompt=prompt,
                )

        demo_url = self.get_demo_concept_image(
            scenario=scenario,
            outfit_name=outfit_name,
            items=items,
            color_palette=color_palette,
            style=style,
            gender=gender,
            variation_index=vidx + 1,
        )
        return GeneratedOutfitImageVariationSchema(
            variation_index=vidx,
            variation_title=title,
            image_url=demo_url,
            status="demo",
            label=IMAGE_DISCLAIMER,
            prompt=prompt,
        )


# Singleton
_image_service: Optional[OutfitImageService] = None

def get_outfit_image_service() -> OutfitImageService:
    global _image_service
    if _image_service is None:
        _image_service = OutfitImageService()
    return _image_service
