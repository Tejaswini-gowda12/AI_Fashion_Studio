import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.models.models import Project, FabricAnalysis

logger = logging.getLogger(__name__)

class DesignAssistantService:
    def generate_response(
        self,
        user_message: str,
        project: Project,
        analysis: Optional[FabricAnalysis] = None
    ) -> Dict[str, Any]:
        garment_type = project.target_garment_type or (analysis.garment_category if analysis else "Garment")
        current_fabric = analysis.fabric_type if analysis else "Conventional Fabric"
        current_weave = analysis.weave if analysis else "woven texture"

        # 1. Try OpenAI if configured
        if settings.OPENAI_API_KEY and settings.AI_LLM_PROVIDER in ["openai", "mock"]:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)

                analysis_context = ""
                if analysis:
                    analysis_context = (
                        f"Current Fabric: {analysis.fabric_type}, Weave: {analysis.weave}, "
                        f"Thickness: {analysis.thickness}, Drape: {analysis.drape}, "
                        f"Dominant Colors: {analysis.dominant_colors}"
                    )

                system_prompt = (
                    "You are an expert AI Sustainable Fashion & Textile Design Assistant. "
                    "Your goal is to guide designers to create eco-friendly garments, recommending sustainable materials "
                    "(e.g., Tencel, Organic Cotton, Hemp, Peace Silk, Piñatex), low-impact dyeing methods, and circular lifecycle practices.\n"
                    "Respond with a JSON object containing two fields:\n"
                    "1. 'response_text': A helpful, well-structured, inspiring markdown message addressing the user.\n"
                    "2. 'structured_concept': (Optional, set to null if not proposing a new garment concept, or an object with keys: "
                    "design_name, inspiration_summary, silhouette, material_recommendation, color_palette (array of 3 hex colors), "
                    "dyeing_method, trims, sustainability_rationale, production_notes)."
                )

                user_prompt = (
                    f"Project Title: {project.title}\n"
                    f"Garment Type: {garment_type}\n"
                    f"Target Season: {project.intended_season or 'All Season'}\n"
                    f"Budget Range: {project.budget_range or 'Medium'}\n"
                    f"{analysis_context}\n\n"
                    f"User Message: {user_message}"
                )

                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=1200
                )

                result_json = json.loads(completion.choices[0].message.content)
                return {
                    "response_text": result_json.get("response_text", ""),
                    "structured_concept": result_json.get("structured_concept")
                }
            except Exception as e:
                logger.warning("OpenAI Design Assistant call failed (%s); falling back to rule-based response.", e)

        # 2. Rule-based fallback
        msg_lower = user_message.lower()
        structured_concept = None

        if "vegan" in msg_lower:
            response_text = (
                f"For a 100% vegan version of this {garment_type}, we eliminate animal-derived fibers (wool, silk, leather) "
                f"and replace them with high-performance plant-based alternatives. \n\n"
                f"**Material Recommendation:** Organic Hemp/Cotton blend or Tencel Lyocell.\n"
                f"**Dyeing Option:** Botanical Natural Dyes or Waterless Digital Ink Printing.\n"
                f"**Trims:** Recycled paper or wooden buttons, GOTS-certified organic cotton sewing thread."
            )
            structured_concept = {
                "design_name": f"Vegan {garment_type} Concept",
                "inspiration_summary": f"Cruelty-free, high-performance redesign of original {garment_type}.",
                "silhouette": f"Modern relaxed {garment_type} silhouette",
                "material_recommendation": "100% Organic Hemp & Linen Blend",
                "color_palette": analysis.dominant_colors if (analysis and analysis.dominant_colors) else ["#2B3A42", "#8A9A86", "#EAD7C3"],
                "dyeing_method": "Low-Impact Fiber-Reactive Dyeing",
                "trims": "Corozo nut buttons and recycled cotton thread",
                "sustainability_rationale": "Zero animal products, 75% lower water consumption, fully biodegradable at end-of-life.",
                "production_notes": "Use zero-waste pattern cutting techniques to minimize cutting room scrap."
            }

        elif "water" in msg_lower:
            response_text = (
                f"To drastically reduce water consumption for your {garment_type} project:\n\n"
                f"1. **Switch Fabric:** Shift from conventional cotton to **Recycled Cotton** or **Organic Hemp**. Hemp requires up to 60% less water to cultivate.\n"
                f"2. **Adopt Dope Dyeing or Waterless Printing:** Adding color pigment during fiber spinning eliminates water-heavy dye bath washings.\n"
                f"3. **Design for Undyed Hues:** Utilizing naturally colored cotton or unbleached linen saves ~8,000 liters per 100 garments."
            )

        elif "texture" in msg_lower or "alternative" in msg_lower:
            response_text = (
                f"To retain the structured {current_weave} texture of your reference image while elevating sustainability:\n\n"
                f"- **Top Recommendation:** **Organic Linen / Hemp Heavy Twill** - mirrors the weight ({analysis.thickness if analysis else 'Medium'}) and drape ({analysis.drape if analysis else 'Moderate'}) perfectly.\n"
                f"- **Secondary Choice:** **Tencel / Lyocell Heavy Canvas** - provides smooth hand-feel with closed-loop solvent processing.\n"
                f"Both alternatives maintain garment structure while eliminating harsh chemical pesticides."
            )

        elif "low-cost" in msg_lower or "production" in msg_lower or "budget" in msg_lower:
            response_text = (
                f"Here is a low-cost, eco-conscious production plan for target budget range ({project.budget_range or 'Medium'}):\n\n"
                f"1. **Sourcing:** Utilize Deadstock Fabric or Recycled Cotton blends to reduce raw material cost by 15-25%.\n"
                f"2. **Dyeing:** Standardize on low-impact reactive dyes in batch runs to lower energy per unit.\n"
                f"3. **Manufacturing:** Modular construction for lower assembly time and standardized trim sizes."
            )
            structured_concept = {
                "design_name": f"Eco-Budget {garment_type}",
                "inspiration_summary": "Cost-optimized sustainable production framework.",
                "silhouette": f"Timeless minimal {garment_type}",
                "material_recommendation": "Recycled Cotton Blend / Upcycled Deadstock",
                "color_palette": ["#1F2937", "#4B5563", "#D1D5DB"],
                "dyeing_method": "Low-Impact Fiber Reactive Batch Dye",
                "trims": "Recycled PET Zippers and Brass Rivets",
                "sustainability_rationale": "Repurposes pre-consumer scrap while minimizing financial overhead.",
                "production_notes": "Local micro-factory assembly with batch dyeing."
            }

        else:
            response_text = (
                f"I've analyzed your project **'{project.title}'** ({garment_type}, {project.intended_season or 'All Season'}).\n\n"
                f"Based on visual characteristics ({current_fabric}, {current_weave}), I recommend focusing on low-water fiber alternatives "
                f"and non-toxic botanical dyeing. How would you like to refine this design concept?"
            )

        return {
            "response_text": response_text,
            "structured_concept": structured_concept
        }
