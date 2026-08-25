# AI Sustainable Fashion Assistant - Fabric Detection & Technical Details Module

An advanced AI and Computer Vision module designed for sustainable fashion applications. Allows designers and users to upload images of garments, textiles, or fabric swatches to automatically infer fabric composition, surface texture, weave/knit structure, pattern classification, dominant color palette, material properties, and comprehensive **Fabric Technical Specifications & Eco Details**.

---

## Features & Capabilities

- **19 Supported Fabric Classes**: Cotton, Organic cotton, Linen, Hemp, Denim, Silk, Peace silk, Wool, Polyester, Recycled polyester, Nylon, Recycled nylon, Rayon/Viscose, Tencel/Lyocell, Bamboo lyocell, Leather, Synthetic blend, Cotton-polyester blend, Unknown.
- **Comprehensive Fabric Details & Specifications**: Automatically provides botanical/synthetic fiber origin, GSM fabric weight, environmental footprint (water consumption in L/kg, carbon emissions in kg CO2e/kg, biodegradability timeline), durability rating, breathability level, washing/care instructions, recognized global certifications (GOTS, OEKO-TEX, European Flax, Fair Trade), ideal garment applications, and pros/cons comparisons.
- **OpenCV + Pillow Computer Vision**: Extracts exact dominant color hex codes, human-readable color names, and percentage distributions using K-Means clustering. Analyzes surface roughness/sharpness via Laplacian variance, shine/gloss, and pattern indicators.
- **Configurable AI Architecture**:
  - `MockFabricDetectionService`: Runs local computer vision analysis with OpenCV/Pillow color and texture metrics without requiring external API keys.
  - `VisionFabricDetectionService`: Integrates with OpenAI GPT-4o Vision or Gemini 1.5/2.0 Vision for real AI multimodal inference with automatic fallback to mock mode.
- **Bounded Certainty & Low Confidence Warnings**: Bounds confidence scores strictly under 1.0 (max 0.95). Triggers a prominent "Unable to identify confidently" banner and suggests top 3 alternative candidate fabrics when confidence is below 0.50.
- **User Correction & Persistence**: Enables manual fabric override with instant saving to database and history tracking.

---

## Detection Output Schema

```json
{
  "garment_type": "shirt",
  "detected_fabric": "Cotton",
  "alternative_possible_fabrics": [
    {"name": "Linen", "confidence": 0.72},
    {"name": "Hemp", "confidence": 0.64}
  ],
  "confidence_score": 0.86,
  "texture": "smooth",
  "weave_or_knit_type": "jersey",
  "pattern": "solid",
  "dominant_colors": [
    {"hex": "#2F4F4F", "name": "Dark Slate Gray", "percentage": 65},
    {"hex": "#E8DCC4", "name": "Cream", "percentage": 35}
  ],
  "material_properties": {
    "thickness": "light",
    "stretch": "medium",
    "shine": "matte",
    "opacity": "opaque",
    "drape": "moderate"
  },
  "sustainability_note": "This result is AI-estimated from visual appearance and should be confirmed through physical testing.",
  "fabric_details": {
    "description": "Natural staple fiber derived from the seed boll of the Gossypium cotton plant...",
    "fiber_origin": "Gossypium Plant Seed Boll",
    "weight_gsm": "140 - 200 GSM (Medium)",
    "water_footprint_liters_per_kg": "9,750 L/kg",
    "carbon_footprint_kg_per_kg": "3.8 kg CO2e/kg",
    "biodegradability_time": "1 - 5 months (Compostable)",
    "durability_rating": 4.0,
    "breathability_level": "High (Moisture absorbent)",
    "care_instructions": "Machine wash warm (40°C), tumble dry medium, iron hot.",
    "certifications": ["OEKO-TEX Standard 100", "Better Cotton Initiative (BCI)"],
    "best_applications": ["T-Shirts", "Casual Shirts", "Bedding", "Underwear"],
    "pros": ["Skin-friendly & soft", "Excellent breathability", "Fully biodegradable"],
    "cons": ["High agricultural water footprint", "Prone to shrinking"]
  }
}
```

---

## Environment Variables Configuration

Create or update `.env` in the `backend` folder:

```env
PROJECT_NAME="AI Sustainable Fabric Analyzer and Fashion Design Assistant"
DATABASE_URL="sqlite:///./sustainable_fashion.db"

# File Upload Settings
MAX_UPLOAD_SIZE_MB=10

# AI Provider Configuration
# Set to 'mock', 'openai', or 'gemini'
AI_VISION_PROVIDER="mock"

# API Keys (Required only if AI_VISION_PROVIDER is set to 'openai' or 'gemini')
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="..."
```

---

## API Documentation

### 1. Analyze Fabric Image
- **Endpoint**: `POST /api/fabric-detection/analyze`
- **Content-Type**: `multipart/form-data`
- **Parameters**: `file` (File, max 10MB, JPG/JPEG/PNG/WebP), `project_id` (Optional int)
- **Response**: `FabricDetectionRecordResponse`

### 2. Get Saved Analysis
- **Endpoint**: `GET /api/fabric-detection/{analysis_id}`
- **Response**: `FabricDetectionRecordResponse`

### 3. Save User Correction
- **Endpoint**: `PATCH /api/fabric-detection/{analysis_id}`
- **Body**:
  ```json
  {
    "user_corrected_fabric": "Organic cotton"
  }
  ```
- **Response**: Updated `FabricDetectionRecordResponse`

### 4. Delete Analysis
- **Endpoint**: `DELETE /api/fabric-detection/{analysis_id}`
- **Response**: `{"message": "Fabric analysis deleted successfully", "id": 1}`

### 5. Get User Analysis History
- **Endpoint**: `GET /api/fabric-detection/history`
- **Response**: `List[FabricDetectionRecordResponse]`

---

## Find Similar Products Online (Visual Web Search)

The system supports reverse-image visual search to discover visually similar products, retail listings, and manufacturer specifications online.

### Strict 3-Tier Clarity Rule
The system strictly separates:
1. **AI Visual Fabric Estimate**: Optical surface texture and weave geometry classification.
2. **Web Visual-Match Results**: Visually similar garments discovered across the web.
3. **Verified Source Page Text**: Fabric information explicitly stated in product specifications on source pages. Web visual similarity never implies confirmed fiber composition.

### Supported Visual Search Providers

Configure the provider in `.env`:
```env
VISUAL_SEARCH_PROVIDER="mock"  # Options: 'mock', 'google_vision', 'bing'
```

#### 1. Mock Provider (`mock` - Default)
- Works out-of-the-box with **no API keys required**.
- Returns realistic mock products from official brands, retailers, and sustainable textile guides with dynamic matching scores.
- Includes both matches with verified composition text and matches marked as unverified.

#### 2. Google Cloud Vision Web Detection (`google_vision`)
- Uses Google Cloud Vision's legal `WEB_DETECTION` API feature.
- **Authentication**:
  - Set `GOOGLE_APPLICATION_CREDENTIALS` to your Google Cloud service account JSON file path, OR
  - Set `GOOGLE_VISION_API_KEY` in your `.env`.
- Requires `google-cloud-vision` Python package (included in `requirements.txt`).

#### 3. Bing Visual Search (`bing`)
- Uses the Microsoft Bing Visual Search REST API.
- **Authentication**:
  - Set `BING_VISUAL_SEARCH_API_KEY` in your `.env`.

### Visual Search API Endpoints

#### POST `/api/visual-search/search`
- **Content-Type**: `multipart/form-data`
- **Parameters**: `file` (UploadFile), `ai_predicted_fabric` (Optional), `garment_category` (Optional), `result_limit` (Optional int, default: 10)
- **Response**:
  ```json
  {
    "search_status": "success",
    "provider_used": "mock",
    "query_context": {
      "ai_predicted_fabric": "Denim",
      "garment_type": "Jacket"
    },
    "matches": [
      {
        "title": "Classic Indigo Denim Jacket",
        "source_url": "https://www.levi.com/...",
        "thumbnail_url": "https://...",
        "source_domain": "levi.com",
        "match_score": 0.93,
        "detected_product_type": "Denim jacket",
        "fabric_text_found": "100% cotton denim, 12 oz. fabric weight",
        "brand": "Levi's",
        "price_text": "$89.50",
        "source_reliability": "official_brand",
        "verification_status": "source_text_found"
      }
    ],
    "related_entities": ["denim jacket", "blue denim", "cotton twill"],
    "disclaimer": "Web matches identify visually similar items only. Fabric composition must be verified through the product label, product page, or supplier specification sheet."
  }
  ```

#### POST `/api/visual-search/save-match`
- Saves a web match to user's saved inspiration collection.

#### GET `/api/visual-search/saved`
- Returns all saved web matches for the current user.

---

## Quick Setup & Execution

### Backend
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

### Running Unit Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173/fabric-detection` to launch the Fabric Detection Workspace.

---

## AI Outfit Studio & Shopping Link Feature

An intelligent outfit concept generator and sustainable shopping discovery engine. Users describe an occasion or scenario, and the AI generates a complete styled look with garment breakdowns, color palettes, fabric recommendations, sustainability scores, styling tips, AI fashion concept art, and curated shopping product matches from authorized sources.

### Key Capabilities

1. **Scenario & Multi-Factor Input**: Accepts occasion descriptions with preferences for gender/style (women, men, unisex), INR budget ranges, sizing, location/country, season/weather, preferred colors/fabrics, and sustainability priorities (vegan, recycled, organic, low-water, low-cost).
2. **Structured Outfit Concepts**: Generates outfit name, occasion, description, garment breakdown (dress/top/bottom/jacket/footwear/bag/accessories with estimated INR costs), palette, fabrics, sustainability breakdown (0-100 score), and styling tips.
3. **AI Outfit Visualization**: Renders an AI fashion visualization concept image clearly labelled *"AI-generated style concept"*, with regenerate, save, and SVG download capabilities.
4. **Authorized Shopping Links**: Curates similar products from legal API-based shopping and authorized search providers (no web scraping) with item image, brand, price in INR, available sizes, fabric details, "Buy Now" external links, and source reliability badges (`official_brand`, `authorized_retailer`, `marketplace`, `mock_demo`).
5. **Interactive UI**: Responsive AI Outfit Studio page with an animated 4-step generation progress pipeline, empty/loading/error states, save-to-profile, and disclosure disclaimers.

### Provider Configuration

Configure providers in `backend/.env`:

```env
# ── AI Outfit Studio ──────────────────────────────────────────────────────────
# LLM Provider: 'mock' (default), 'gemini', or 'openai'
OUTFIT_LLM_PROVIDER="mock"

# Image Provider: 'mock' (default SVG fashion boards), 'dalle', or 'gemini'
OUTFIT_IMAGE_PROVIDER="mock"

# Shopping Provider: 'mock' (default curated catalog) or 'google_cse'
OUTFIT_SHOPPING_PROVIDER="mock"

# Google Custom Search API (Required only if OUTFIT_SHOPPING_PROVIDER='google_cse')
GOOGLE_CUSTOM_SEARCH_API_KEY="AIza..."
GOOGLE_CUSTOM_SEARCH_CX="0123456789..."

# Rate Limits & Quotas
OUTFIT_SEARCH_RESULT_LIMIT=8
OUTFIT_RATE_LIMIT_PER_MIN=5
OUTFIT_IMAGE_QUOTA_PER_USER_PER_DAY=10
```

### AI Outfit Studio API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/outfit/generate` | Generate outfit concept, image & shopping links | No (Public) |
| `POST` | `/api/outfit/{id}/regenerate-image` | Regenerate outfit concept image | No |
| `GET` | `/api/outfit/{id}` | Retrieve specific outfit generation | No |
| `GET` | `/api/outfit/history` | Get authenticated user's generation history | Yes |
| `POST` | `/api/outfit/{id}/save` | Save outfit generation to profile | Yes |
| `GET` | `/api/outfit/saved` | List user's saved outfits | Yes |
| `DELETE` | `/api/outfit/saved/{saved_id}` | Remove an outfit from saved list | Yes |

---

## Physical Testing Disclaimer

> [!WARNING]
> Visual appearance alone cannot determine exact fiber blend composition. All AI predictions returned by this system are estimations based on visual surface features and color spectrums. Physical burn tests, chemical solubility tests, or spectroscopic analysis should be conducted to confirm textile fiber composition prior to commercial manufacturing.

