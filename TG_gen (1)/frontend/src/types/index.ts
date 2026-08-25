export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'user' | 'admin';
  sustainability_preferences?: Record<string, any>;
  preferred_materials?: string[];
  created_at: string;
}

export interface ReferenceImage {
  id: number;
  project_id: number;
  file_path: string;
  original_filename: string;
  created_at: string;
}

export interface Project {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  target_garment_type?: string;
  intended_season?: string;
  target_audience?: string;
  budget_range?: string;
  sustainability_goal?: string;
  created_at: string;
  updated_at: string;
  reference_images?: ReferenceImage[];
}

export interface DominantColorItem {
  hex: string;
  name: string;
  percentage: number;
}

export interface AlternativeFabricItem {
  name: string;
  confidence: number;
}

export interface MaterialPropertiesObject {
  thickness: 'light' | 'medium' | 'heavy' | string;
  stretch: 'low' | 'medium' | 'high' | string;
  shine: 'matte' | 'semi-gloss' | 'glossy' | string;
  opacity: 'sheer' | 'semi-sheer' | 'opaque' | string;
  drape: 'structured' | 'moderate' | 'fluid' | string;
}

export interface FabricDetails {
  description: string;
  fiber_origin: string;
  weight_gsm: string;
  water_footprint_liters_per_kg: string;
  carbon_footprint_kg_per_kg: string;
  biodegradability_time: string;
  durability_rating: number;
  breathability_level: string;
  care_instructions: string;
  certifications: string[];
  best_applications: string[];
  pros: string[];
  cons: string[];
}

export interface FabricDetectionRecord {
  id: number;
  user_id?: number;
  image_url: string;
  garment_type: string;
  detected_fabric: string;
  confidence_score: number;
  alternative_possible_fabrics: AlternativeFabricItem[];
  texture: string;
  weave_or_knit_type: string;
  pattern: string;
  dominant_colors: DominantColorItem[];
  material_properties: MaterialPropertiesObject;
  sustainability_note?: string;
  user_corrected_fabric?: string;
  fabric_details?: FabricDetails;
  created_at: string;
  updated_at?: string;
}

export interface FabricAnalysis {
  id: number;
  reference_image_id?: number;
  user_id?: number;
  image_url?: string;
  garment_category?: string;
  garment_type?: string;
  fabric_type?: string;
  detected_fabric?: string;
  dominant_colors: any[];
  secondary_colors?: any[];
  pattern_type?: string;
  pattern?: string;
  weave?: string;
  weave_or_knit_type?: string;
  texture?: string;
  shine?: string;
  thickness?: string;
  stretch?: string;
  drape?: string;
  opacity?: string;
  material_properties?: MaterialPropertiesObject;
  alternative_possible_fabrics?: AlternativeFabricItem[];
  sustainability_note?: string;
  ai_note?: string;
  confidence_score: number;
  is_user_corrected?: boolean;
  user_corrected_fabric?: string;
  fabric_details?: FabricDetails;
  created_at: string;
  updated_at?: string;
}

export interface Fabric {
  id: number;
  name: string;
  category: string;
  fiber_source: string;
  water_impact_score: number;
  carbon_impact_score: number;
  biodegradability_score: number;
  cost_level: string;
  durability_rating: number;
  comfort_rating: number;
  is_vegan: boolean;
  is_recyclable: boolean;
  texture_tags: string[];
  pros: string[];
  limitations: string[];
  best_use_cases: string[];
  is_active: boolean;
}

export interface DyeMethod {
  id: number;
  name: string;
  process_type: string;
  water_impact_level: string;
  energy_impact_level: string;
  cost_level: string;
  color_accuracy_rating: number;
  limitation_notes?: string;
  suitable_fabrics: string[];
  is_active: boolean;
}

export interface PriorityWeights {
  lowest_cost: number;
  closest_appearance: number;
  low_water: number;
  low_carbon: number;
  recyclability: number;
  vegan: number;
  durability: number;
}

export interface FabricRecommendation {
  fabric: Fabric;
  match_percentage: number;
  calculation_breakdown: {
    eco_score: number;
    appearance_similarity: number;
    water_impact_score: number;
    carbon_impact_score: number;
    cost_level: string;
    durability_rating: number;
  };
  match_reasons: string[];
}

export interface DyeRecommendation {
  dye_method: DyeMethod;
  compatibility: string;
  color_accuracy: string;
  water_impact: string;
  energy_impact: string;
  estimated_cost: string;
  recommendation_rationale: string;
}

export interface ImpactAssessment {
  analysis_id: number;
  conventional_fabric: string;
  selected_fabric: string;
  conventional_dye: string;
  selected_dye: string;
  water_saved_liters: number;
  co2_reduced_kg: number;
  waste_reduced_kg: number;
  chemical_reduction_pct: number;
  summary_text: string;
  assumptions: string[];
  water_comparison: {
    conventional: number;
    sustainable: number;
  };
  co2_comparison: {
    conventional: number;
    sustainable: number;
  };
}

export interface DesignConcept {
  id: number;
  project_id: number;
  design_name: string;
  inspiration_summary?: string;
  silhouette?: string;
  material_recommendation?: string;
  color_palette?: string[];
  dyeing_method?: string;
  trims?: string;
  sustainability_rationale?: string;
  production_notes?: string;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  project_id: number;
  user_id: number;
  sender: 'user' | 'assistant';
  content: string;
  metadata_json?: {
    structured_concept?: Partial<DesignConcept>;
  };
  created_at: string;
}

export interface GeneratedImage {
  id: number;
  concept_id?: number;
  project_id: number;
  prompt: string;
  image_url: string;
  generation_mode: string;
  created_at: string;
}

export interface TopPredictionItem {
  fabric: string;
  confidence: number;
}

export interface VisibleFeatures {
  texture: string;
  weave: string;
  pattern: string;
  thickness: string;
  shine: string;
  stretch: string;
  opacity: string;
}

// ── Image quality validation types ──────────────────────────────────────────
export interface CheckDetail {
  passed: boolean;
  actual?: string;
  required?: string;
  message: string;
}

export interface ImageQualityChecks {
  resolution: CheckDetail;
  blur: CheckDetail;
  lighting: CheckDetail;
  fabric_coverage: CheckDetail;
}

export interface ImageQualityMetrics {
  // Structured (new) fields
  is_valid: boolean;
  quality_score: number;        // integer 0-100
  checks: ImageQualityChecks;
  user_guidance: string[];
  // Backward-compatible flat aliases
  score?: number;               // float 0-1 (quality_score / 100)
  blur?: string;                // "low" | "medium" | "high"
  lighting?: string;            // "good" | "under-exposed" | "over-exposed"
  fabric_coverage?: number;     // float 0-1
  min_resolution_passed?: boolean;
  warning?: string | null;
}

export interface FabricAnalyzeResponse {
  id?: number;
  predicted_fabric: string;
  // Confidence — both spellings for compatibility
  confidence?: number;
  confidence_score: number;
  // Status — both spellings
  status?: string;
  prediction_status: 'high_confidence' | 'uncertain' | string;
  top_predictions: TopPredictionItem[];
  // Rich AI explanation
  explanation?: string;
  visible_features: VisibleFeatures;
  image_quality: ImageQualityMetrics;
  limitations: string;
  recommended_next_step?: string;
  fabric_details?: FabricDetails;
  user_corrected_fabric?: string;
  is_user_corrected?: boolean;
  /** Set to true on the frontend when user clicked "Continue Anyway" for a borderline image */
  is_lower_confidence?: boolean;
  image_url?: string;
  created_at?: string;
}

export interface ModelVersion {
  id: number;
  version: string;
  model_name: string;
  dataset_size: number;
  physical_samples_count: number;
  accuracy: number;
  macro_f1: number;
  precision: number;
  recall: number;
  confusion_matrix: number[][];
  class_metrics: Record<string, { precision: number; recall: number; f1_score: number; test_samples: number }>;
  condition_metrics: Record<string, { accuracy: number; samples: number; description: string }>;
  is_active: boolean;
  evaluation_date: string;
  created_at: string;
}

export interface ModelMetricsResponse {
  active_model: ModelVersion;
  all_versions: ModelVersion[];
  dataset_stats: {
    total_images: number;
    physical_fabric_samples: number;
    train_split: number;
    val_split: number;
    test_split: number;
    target_validation_accuracy: number;
    class_count: number;
    supported_classes: string[];
  };
}

export interface PredictionFeedback {
  id?: number;
  analysis_id?: number;
  predicted_fabric: string;
  corrected_fabric: string;
  verified_composition?: string;
  physical_test_method?: string;
  image_quality_rating?: number;
  feedback_notes?: string;
  created_at?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Visual Search Types
// ─────────────────────────────────────────────────────────────────────────────

/** Source reliability classification for a web match result. */
export type SourceReliability = 'official_brand' | 'retailer' | 'blog_editorial' | 'unknown';

/** Verification status: whether the source page explicitly states composition. */
export type VerificationStatus = 'source_text_found' | 'not_verified';

/** Active filter for the VisualSearchResults filter bar. */
export type VisualSearchFilter = 'all' | 'official' | 'products' | 'fabric_refs' | 'top_match';

/** A single web visual-match result from POST /api/visual-search/search */
export interface VisualSearchMatch {
  id?: number;
  title?: string;
  source_url: string;
  thumbnail_url?: string;
  source_domain?: string;
  match_score: number;
  detected_product_type?: string;
  /** Explicitly stated fabric composition from the source page — null if not found */
  fabric_text_found?: string | null;
  brand?: string;
  price_text?: string;
  source_reliability: SourceReliability;
  verification_status: VerificationStatus;
}

/** AI-derived context used to guide the web search query. */
export interface VisualSearchQueryContext {
  ai_predicted_fabric?: string;
  garment_type?: string;
}

/** Top-level response from POST /api/visual-search/search */
export interface VisualSearchResponse {
  search_id?: number;
  search_status: 'success' | 'failed' | 'no_results';
  provider_used: string;
  query_context: VisualSearchQueryContext;
  matches: VisualSearchMatch[];
  related_entities: string[];
  disclaimer: string;
}

/** Request body to save a web match as project inspiration. */
export interface SaveMatchRequest {
  visual_search_match_id?: number;
  project_id?: number;
  title?: string;
  source_url: string;
  thumbnail_url?: string;
  source_domain?: string;
  source_reliability?: SourceReliability;
  fabric_text_found?: string | null;
  match_score?: number;
}

/** A previously saved web match record. */
export interface SavedWebMatch {
  id: number;
  user_id?: number;
  visual_search_match_id?: number;
  project_id?: number;
  title?: string;
  source_url: string;
  thumbnail_url?: string;
  source_domain?: string;
  source_reliability: SourceReliability;
  fabric_text_found?: string | null;
  match_score: number;
  saved_at: string;
}
