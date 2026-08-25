import os
import base64
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from PIL import Image

logger = logging.getLogger(__name__)

class VisionAnalyzerInterface(ABC):
    @abstractmethod
    def analyze_image(self, file_path: str) -> Dict[str, Any]:
        pass

class MockVisionAnalyzer(VisionAnalyzerInterface):
    def analyze_image(self, file_path: str) -> Dict[str, Any]:
        garment_categories = ["Denim Jacket", "Summer Dress", "Casual T-Shirt", "Structured Blazer", "Knit Sweater", "Overcoat", "Trousers"]
        fabric_types = ["Conventional Heavy Denim", "Cotton Canvas", "Silk Satin", "Polyester Blend Twill", "Wool Flannel", "Linen Weave", "Ribbed Jersey"]
        patterns = ["Solid", "Twill Weave", "Subtle Stripe", "Textured Knit", "Melange", "Heathered"]
        weaves = ["Twill", "Plain Weave", "Satin", "Knit", "Jacquard", "Herringbone"]
        shines = ["Matte", "Low Shine", "Satin Sheen", "Glossy"]
        thicknesses = ["Lightweight", "Medium", "Heavyweight"]
        stretches = ["None", "Low", "Medium", "High"]
        drapes = ["Stiff", "Moderate", "Fluid"]
        opacities = ["Opaque", "Semi-Opaque", "Sheer"]

        dominant_colors = ["#2B3A42", "#8A9A86"]
        secondary_colors = ["#C86D51", "#EAD7C3"]

        try:
            if os.path.exists(file_path):
                with Image.open(file_path) as img:
                    img_rgb = img.convert('RGB')
                    colors = img_rgb.getcolors(maxcolors=1024*1024)
                    if colors:
                        sorted_colors = sorted(colors, key=lambda item: item[0], reverse=True)
                        top_rgb = [c[1] for c in sorted_colors[:4]]
                        dominant_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in top_rgb[:2]]
                        secondary_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in top_rgb[2:4]]
        except Exception:
            pass

        file_hash = sum(ord(c) for c in os.path.basename(file_path))
        
        garment_cat = garment_categories[file_hash % len(garment_categories)]
        fab_type = fabric_types[file_hash % len(fabric_types)]
        pattern = patterns[file_hash % len(patterns)]
        weave = weaves[file_hash % len(weaves)]
        shine = shines[file_hash % len(shines)]
        thickness = thicknesses[file_hash % len(thicknesses)]
        stretch = stretches[file_hash % len(stretches)]
        drape = drapes[file_hash % len(drapes)]
        opacity = opacities[file_hash % len(opacities)]
        confidence = round(0.88 + (file_hash % 10) * 0.01, 2)

        return {
            "garment_category": garment_cat,
            "fabric_type": fab_type,
            "dominant_colors": dominant_colors,
            "secondary_colors": secondary_colors,
            "pattern_type": pattern,
            "weave": weave,
            "shine": shine,
            "thickness": thickness,
            "stretch": stretch,
            "drape": drape,
            "opacity": opacity,
            "confidence_score": confidence
        }

class OpenAIVisionAnalyzer(VisionAnalyzerInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.mock_fallback = MockVisionAnalyzer()

    def analyze_image(self, file_path: str) -> Dict[str, Any]:
        if not self.api_key or not os.path.exists(file_path):
            return self.mock_fallback.analyze_image(file_path)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

            ext = os.path.splitext(file_path)[1].lower().replace(".", "")
            mime = f"image/{ext}" if ext in ["png", "jpeg", "jpg", "webp"] else "image/jpeg"

            prompt = (
                "Analyze this fashion garment or textile image in detail. Return ONLY a valid JSON object with the following fields:\n"
                "- garment_category: string (e.g. Blazer, Dress, T-Shirt, Trousers, Swatch)\n"
                "- fabric_type: string (e.g. Heavy Cotton Twill, Silk Satin, Linen, Wool Flannel)\n"
                "- dominant_colors: array of 2 hex color strings (e.g. ['#2B3A42', '#8A9A86'])\n"
                "- secondary_colors: array of 2 hex color strings\n"
                "- pattern_type: string (e.g. Solid, Striped, Plaid, Houndstooth)\n"
                "- weave: string (e.g. Plain Weave, Twill, Satin, Ribbed Knit)\n"
                "- shine: string (e.g. Matte, Subtle Sheen, Glossy)\n"
                "- thickness: string (e.g. Lightweight, Medium, Heavyweight)\n"
                "- stretch: string (e.g. None, Low, Medium, High)\n"
                "- drape: string (e.g. Stiff, Moderate, Fluid)\n"
                "- opacity: string (e.g. Opaque, Semi-Opaque, Sheer)\n"
                "- confidence_score: float between 0.80 and 0.99\n"
            )

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{encoded_string}"
                                },
                            },
                        ],
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
            )

            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.warning("OpenAI Vision analysis failed (%s); falling back to mock analyzer.", e)
            return self.mock_fallback.analyze_image(file_path)

def get_vision_analyzer(provider: str = "mock", api_key: str = "") -> VisionAnalyzerInterface:
    if provider == "openai" and api_key:
        return OpenAIVisionAnalyzer(api_key=api_key)
    return MockVisionAnalyzer()
