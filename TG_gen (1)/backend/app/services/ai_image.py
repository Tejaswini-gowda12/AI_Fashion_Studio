import os
import base64
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.models.models import Project, DesignConcept, FabricAnalysis

logger = logging.getLogger(__name__)

class ConceptImageGenerator:
    def generate_concept_image(
        self,
        project: Project,
        concept: Optional[DesignConcept] = None,
        analysis: Optional[FabricAnalysis] = None,
        custom_prompt_suffix: str = ""
    ) -> Dict[str, Any]:
        garment = project.target_garment_type or (analysis.garment_category if analysis else "Fashion Garment")
        material = concept.material_recommendation if concept else (analysis.fabric_type if analysis else "Sustainable Linen")
        dye = concept.dyeing_method if concept else "Natural Plant Dye"
        colors = concept.color_palette if (concept and concept.color_palette) else (analysis.dominant_colors if (analysis and analysis.dominant_colors) else ["#2B3A42", "#8A9A86", "#C86D51"])

        color_primary = colors[0] if len(colors) > 0 else "#2B3A42"
        color_secondary = colors[1] if len(colors) > 1 else "#8A9A86"
        color_accent = colors[2] if len(colors) > 2 else "#C86D51"

        prompt = (
            f"High-end fashion editorial render of a sustainable {garment}, crafted from organic {material}, "
            f"dyed with eco-friendly {dye}. Colors: {', '.join(colors)}. Soft natural lighting, studio portrait, 8k resolution. "
            f"{custom_prompt_suffix}"
        ).strip()

        # Try DALL-E if provider is openai and key is present
        if settings.OPENAI_API_KEY and settings.AI_IMAGE_PROVIDER in ["openai", "dalle"]:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"{prompt} Clean studio background, ultra realistic garment detail, no logos or text.",
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                image_url = response.data[0].url
                return {
                    "prompt": prompt,
                    "image_url": image_url,
                    "generation_mode": "openai-dalle-3"
                }
            except Exception as e:
                logger.warning("OpenAI DALL-E image generation failed (%s); generating high-resolution SVG concept instead.", e)

        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="750" viewBox="0 0 600 750" style="background:#181A1B; font-family: sans-serif;">
            <defs>
                <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{color_primary}" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#121314" stop-opacity="0.95"/>
                </linearGradient>
                <linearGradient id="garmentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{color_secondary}"/>
                    <stop offset="100%" stop-color="{color_primary}"/>
                </linearGradient>
            </defs>

            <rect width="600" height="750" fill="url(#bgGrad)" rx="16"/>
            
            <line x1="40" y1="40" x2="560" y2="40" stroke="#8A9A86" stroke-opacity="0.2" stroke-width="1"/>
            <line x1="40" y1="710" x2="560" y2="710" stroke="#8A9A86" stroke-opacity="0.2" stroke-width="1"/>

            <rect x="40" y="60" width="160" height="32" rx="16" fill="#1C3A27" stroke="#8A9A86" stroke-width="1"/>
            <text x="120" y="81" font-size="12" fill="#8A9A86" font-weight="bold" text-anchor="middle">AI ECO CONCEPT</text>

            <g transform="translate(150, 140)">
                <path d="M 110 40 L 150 20 L 190 40 Z" fill="none" stroke="{color_accent}" stroke-width="3"/>
                <path d="M 80 70 Q 150 50 220 70 L 250 220 L 220 420 L 80 420 L 50 220 Z" 
                      fill="url(#garmentGrad)" stroke="{color_accent}" stroke-width="2" opacity="0.9"/>
                <line x1="90" y1="120" x2="210" y2="120" stroke="#ffffff" stroke-opacity="0.15" stroke-width="2"/>
                <line x1="85" y1="180" x2="215" y2="180" stroke="#ffffff" stroke-opacity="0.15" stroke-width="2"/>
                <line x1="80" y1="240" x2="220" y2="240" stroke="#ffffff" stroke-opacity="0.15" stroke-width="2"/>
                <line x1="80" y1="300" x2="220" y2="300" stroke="#ffffff" stroke-opacity="0.15" stroke-width="2"/>
                <line x1="80" y1="360" x2="220" y2="360" stroke="#ffffff" stroke-opacity="0.15" stroke-width="2"/>
            </g>

            <rect x="40" y="580" width="520" height="110" rx="12" fill="#222525" stroke="#374151" stroke-width="1"/>
            <text x="60" y="612" font-size="18" fill="#F9F7F1" font-weight="bold">{concept.design_name if concept else garment}</text>
            <text x="60" y="638" font-size="13" fill="#9CA3AF">Material: {material}</text>
            <text x="60" y="660" font-size="13" fill="#9CA3AF">Dyeing Method: {dye}</text>

            <circle cx="480" cy="630" r="14" fill="{color_primary}" stroke="#FFFFFF" stroke-width="1.5"/>
            <circle cx="510" cy="630" r="14" fill="{color_secondary}" stroke="#FFFFFF" stroke-width="1.5"/>
            <circle cx="540" cy="630" r="14" fill="{color_accent}" stroke="#FFFFFF" stroke-width="1.5"/>
            <text x="510" y="665" font-size="10" fill="#8A9A86" text-anchor="middle">Eco Palette</text>
        </svg>'''

        b64_svg = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        image_data_url = f"data:image/svg+xml;base64,{b64_svg}"

        return {
            "prompt": prompt,
            "image_url": image_data_url,
            "generation_mode": "mock"
        }
