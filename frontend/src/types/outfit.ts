// TypeScript interfaces for the AI Outfit Studio feature

export interface OutfitGenerateRequest {
  scenario: string;
  gender_preference?: 'women' | 'men' | 'unisex' | 'no_preference';
  budget_inr?: number;
  is_budget_friendly?: boolean;
  budget_tier?: 'budget_friendly' | 'balanced' | 'premium';
  size?: string;
  location?: string;
  weather_season?: string;
  preferred_colors?: string[];
  preferred_fabrics?: string[];
  sustainability_preferences?: string[];
  style?: 'casual' | 'formal' | 'traditional' | 'party' | 'streetwear' | 'minimal' | 'luxury';
  reference_image_path?: string;
}

export interface OutfitItem {
  id?: number;
  category: string;
  name: string;
  search_query?: string;
  preferred_fabric?: string;
  recommended_fabric?: string;
  color?: string;
  estimated_budget_inr?: number;
  estimated_price_inr?: number;
  sustainability_note?: string;
}

export interface Outfit {
  name?: string;
  outfit_name: string;
  occasion?: string;
  description: string;
  items: OutfitItem[];
  color_palette: string[];
  recommended_fabrics: string[];
  sustainability_summary?: string;
  sustainability_score?: number;
  styling_tips: string[];
  total_estimated_price_inr?: number;
}

export interface GeneratedImageInfo {
  url?: string | null;
  status: 'generated' | 'demo' | 'unavailable';
  disclaimer: string;
  message?: string | null;
  prompt?: string | null;
}

export interface GeneratedOutfitImageVariation {
  id?: number;
  variation_index: number;
  variation_title: string;
  image_url: string;
  status: 'generated' | 'demo' | 'unavailable';
  label: string;
  prompt?: string | null;
  created_at?: string;
}

export interface RetailerSearchLink {
  retailer: 'Myntra' | 'AJIO' | 'Nykaa Fashion' | 'Amazon India' | 'Tata CLiQ' | string;
  search_url: string;
  query: string;
  icon?: string;
}

export interface ShoppingMatch {
  id?: number;
  retailer: 'Myntra' | 'AJIO' | 'Nykaa Fashion' | 'Amazon India' | 'Tata CLiQ' | 'Official Brand' | string;
  category?: string;
  title: string;
  brand?: string;
  price_inr?: number;
  price?: number;
  currency: string;
  product_url: string;
  image_url?: string;
  fabric_details?: string;
  available_sizes: string[];
  match_score: number;
  data_source: 'affiliate_feed' | 'official_api' | 'approved_search' | 'mock_demo';
  source_type: 'official_brand' | 'authorized_retailer' | 'marketplace' | 'mock_demo';
  status: 'verified' | 'demo';
  timestamp?: string;
  sustainability_label?: string;
}

export interface OutfitGenerateResponse {
  generation_id: number;
  outfit: Outfit;
  generated_image: GeneratedImageInfo;
  generated_images: GeneratedOutfitImageVariation[];
  generated_image_url?: string;
  generated_image_id?: number;
  image_label: string;
  shopping_results: ShoppingMatch[];
  shopping_matches: ShoppingMatch[];
  retailer_search_links: RetailerSearchLink[];
  provider_info: Record<string, string>;
  disclaimer: string;
  store_verification_notice: string;
  is_mock_mode: boolean;
}

export interface SavedOutfit {
  id: number;
  user_id: number;
  generation_id: number;
  project_id?: number;
  notes?: string;
  saved_at: string;
}

export interface OutfitHistoryItem {
  generation_id: number;
  outfit_name?: string;
  scenario: string;
  style?: string;
  gender_preference?: string;
  budget_inr?: number;
  total_estimated_price_inr?: number;
  generated_image_url?: string;
  sustainability_score?: number;
  created_at: string;
}

export type GenerationStatus = 'idle' | 'analyzing' | 'styling' | 'visualizing' | 'shopping' | 'done' | 'error';

export const GENERATION_STEPS: { key: GenerationStatus; label: string; description: string }[] = [
  { key: 'analyzing',   label: 'Analyzing Scenario',    description: 'Understanding your occasion and fashion style...' },
  { key: 'styling',     label: 'Designing Outfit',      description: 'Selecting sustainable fabrics, colors & drape...' },
  { key: 'visualizing', label: 'Generating Variations', description: 'Rendering realistic fashion concept visualizations...' },
  { key: 'shopping',    label: 'Connecting Stores',     description: 'Gathering verified products & Indian store links...' },
];

export const STYLE_OPTIONS = [
  { value: 'casual',       label: 'Casual',       icon: '👕' },
  { value: 'formal',       label: 'Formal',       icon: '👔' },
  { value: 'traditional',  label: 'Traditional',  icon: '🪡' },
  { value: 'party',        label: 'Party',        icon: '✨' },
  { value: 'streetwear',   label: 'Streetwear',   icon: '🎒' },
  { value: 'minimal',      label: 'Minimal',      icon: '⬜' },
  { value: 'luxury',       label: 'Luxury',       icon: '👑' },
];

export const GENDER_OPTIONS = [
  { value: 'women',         label: 'Women' },
  { value: 'men',           label: 'Men' },
  { value: 'unisex',        label: 'Unisex' },
  { value: 'no_preference', label: 'No Preference' },
];

export const SUSTAINABILITY_OPTIONS = [
  { value: 'vegan',            label: 'Vegan',            color: '#4ade80' },
  { value: 'recycled',         label: 'Recycled',         color: '#60a5fa' },
  { value: 'organic',          label: 'Organic',          color: '#86efac' },
  { value: 'low water impact', label: 'Low Water',        color: '#38bdf8' },
  { value: 'low-cost',         label: 'Budget-friendly',  color: '#fbbf24' },
  { value: 'handcrafted',      label: 'Handcrafted',      color: '#c084fc' },
  { value: 'biodegradable',    label: 'Biodegradable',    color: '#a3e635' },
];

export const WEATHER_OPTIONS = [
  'Summer', 'Winter', 'Monsoon', 'Spring', 'Autumn', 'All Season'
];

export const COLOR_PRESETS = [
  { name: 'Sage Green',  hex: '#7D9B76' },
  { name: 'Ivory',       hex: '#F8F1E4' },
  { name: 'Terracotta',  hex: '#C86D51' },
  { name: 'Navy',        hex: '#1C2B4B' },
  { name: 'Dusty Rose',  hex: '#D4A5A5' },
  { name: 'Charcoal',    hex: '#3A3A3A' },
  { name: 'Cream',       hex: '#F5F0E8' },
  { name: 'Olive',       hex: '#6B7B3A' },
  { name: 'Indigo',      hex: '#4A6FA5' },
  { name: 'Blush',       hex: '#F4C2C2' },
];

export const FABRIC_PRESETS = [
  'Tencel/Lyocell', 'Organic Cotton', 'Hemp', 'Linen', 'Bamboo',
  'Recycled Polyester', 'Deadstock', 'Chanderi', 'Khadi', 'Cork'
];

export const CATEGORY_ICONS: Record<string, string> = {
  Dress:     '👗',
  Top:       '👕',
  Bottom:    '👖',
  Jacket:    '🧥',
  Footwear:  '👞',
  Bag:       '👜',
  Accessory: '✨',
};

export const getItemCategoryIcon = (category: string = '', itemName: string = '', gender?: string): string => {
  const cat = category.toLowerCase();
  const name = itemName.toLowerCase();
  const isMen = gender === 'men' || name.includes('men') || name.includes('oxford') || name.includes('brogue') || name.includes('suit') || name.includes('trousers') || name.includes('cufflink') || name.includes('tie') || name.includes('kurta');
  const isWomen = gender === 'women' || name.includes('women') || name.includes('dress') || name.includes('gown') || name.includes('anarkali') || name.includes('heels') || name.includes('jhumka') || name.includes('skirt') || name.includes('dupatta');

  if (cat.includes('dress') || name.includes('dress') || name.includes('anarkali') || name.includes('gown') || name.includes('saree')) {
    return '👗';
  }
  if (cat.includes('suit') || name.includes('suit') || name.includes('tuxedo')) {
    return '🤵';
  }
  if (cat.includes('jacket') || cat.includes('blazer') || cat.includes('coat') || name.includes('jacket') || name.includes('blazer') || name.includes('bundi')) {
    return '🧥';
  }
  if (cat.includes('top') || cat.includes('shirt') || name.includes('shirt') || name.includes('tee') || name.includes('kurta')) {
    return isMen ? '👔' : isWomen ? '👚' : '👕';
  }
  if (cat.includes('bottom') || cat.includes('pant') || cat.includes('trouser') || cat.includes('jeans') || name.includes('trouser') || name.includes('jeans') || name.includes('churidar') || name.includes('pyjama')) {
    return '👖';
  }
  if (cat.includes('shoe') || cat.includes('footwear') || name.includes('shoe') || name.includes('sneaker') || name.includes('brogue') || name.includes('heel') || name.includes('jutti')) {
    if (isMen || name.includes('oxford') || name.includes('brogue') || name.includes('loafer') || name.includes('kolhapuri')) return '👞';
    if (isWomen || name.includes('heel') || name.includes('pump') || name.includes('sandal')) return '👠';
    return '👟';
  }
  if (cat.includes('bag') || name.includes('bag') || name.includes('backpack') || name.includes('tote')) {
    return isMen || name.includes('backpack') ? '🎒' : '👜';
  }
  if (cat.includes('access') || name.includes('watch') || name.includes('tie') || name.includes('cufflink') || name.includes('ring') || name.includes('jewel') || name.includes('earring') || name.includes('dupatta')) {
    if (name.includes('tie') || name.includes('cufflink')) return '👔';
    if (name.includes('watch')) return '⌚';
    return isMen ? '⌚' : '💎';
  }
  return '✨';
};

export const SOURCE_TYPE_LABELS: Record<string, { label: string; color: string }> = {
  official_brand:       { label: 'Official Brand',       color: '#4ade80' },
  authorized_retailer:  { label: 'Authorized Retailer',  color: '#60a5fa' },
  marketplace:          { label: 'Marketplace',          color: '#fbbf24' },
  mock_demo:            { label: 'Demo Result',          color: '#9ca3af' },
};

export const RETAILER_BADGES: Record<string, { label: string; bg: string; text: string; border: string }> = {
  Myntra:          { label: 'Myntra',          bg: 'bg-rose-50 dark:bg-rose-950/40',       text: 'text-rose-700 dark:text-rose-300',       border: 'border-rose-200 dark:border-rose-800' },
  AJIO:            { label: 'AJIO',            bg: 'bg-amber-50 dark:bg-amber-950/40',     text: 'text-amber-700 dark:text-amber-300',     border: 'border-amber-200 dark:border-amber-800' },
  'Nykaa Fashion': { label: 'Nykaa Fashion',   bg: 'bg-pink-50 dark:bg-pink-950/40',       text: 'text-pink-700 dark:text-pink-300',       border: 'border-pink-200 dark:border-pink-800' },
  'Amazon India':  { label: 'Amazon India',    bg: 'bg-orange-50 dark:bg-orange-950/40',   text: 'text-orange-700 dark:text-orange-300',   border: 'border-orange-200 dark:border-orange-800' },
  'Tata CLiQ':     { label: 'Tata CLiQ',       bg: 'bg-indigo-50 dark:bg-indigo-950/40',   text: 'text-indigo-700 dark:text-indigo-300',   border: 'border-indigo-200 dark:border-indigo-800' },
  Flipkart:        { label: 'Flipkart',        bg: 'bg-blue-50 dark:bg-blue-950/40',       text: 'text-blue-700 dark:text-blue-300',       border: 'border-blue-200 dark:border-blue-800' },
  'Official Brands':{ label: 'Official Brands',bg: 'bg-emerald-50 dark:bg-emerald-950/40', text: 'text-emerald-700 dark:text-emerald-300', border: 'border-emerald-200 dark:border-emerald-800' },
  'Official Brand':{ label: 'Official Brand',  bg: 'bg-emerald-50 dark:bg-emerald-950/40', text: 'text-emerald-700 dark:text-emerald-300', border: 'border-emerald-200 dark:border-emerald-800' },
};

export const SCENARIO_EXAMPLES = [
  'Full-body editorial fashion look with a sustainable sage-green Tencel wrap midi dress for a summer formal office setting',
  'Eco-friendly college farewell party outfit with elegant modest drape',
  'Handcrafted festive Chanderi silk anarkali wedding guest look under ₹5,000',
  'Casual organic denim and indigo hemp shirt for a weekend trip',
  "Men's sustainable interview formal set with bamboo lyocell shirt",
];

// ─────────────────────────────────────────────────────────────────────────────
// Compare Prices & Buy Similar Styles Interfaces
// ─────────────────────────────────────────────────────────────────────────────

export interface ProductResult {
  id: string;
  outfit_item: string;
  title: string;
  retailer: string;
  product_url: string;
  image_url?: string | null;
  current_price_inr?: number | null;
  original_price_inr?: number | null;
  discount_percent?: number | null;
  fabric_details?: string | null;
  sustainability_details?: string | null;
  match_score: number;
  data_source: string;
  status: 'verified' | 'demo' | string;
  last_updated_at: string;
}

export interface BestDealInfo {
  best_price_product?: ProductResult | null;
  best_sustainable_product?: ProductResult | null;
  estimated_savings_inr?: number | null;
  next_cheapest_price_inr?: number | null;
  verified_source_label: string;
  has_verified_savings: boolean;
}

export interface PriceComparisonResponse {
  outfit_item?: string;
  total_products: number;
  best_deal?: BestDealInfo | null;
  products: ProductResult[];
  retailer_fallback_links: RetailerSearchLink[];
  is_demo_mode: boolean;
  disclaimer: string;
}

export interface PriceSnapshot {
  price_inr: number;
  original_price_inr?: number | null;
  is_verified: boolean;
  recorded_at: string;
}

export interface PriceHistoryResponse {
  product_id: string;
  retailer?: string;
  current_price_inr?: number | null;
  lowest_price_inr?: number | null;
  highest_price_inr?: number | null;
  snapshots: PriceSnapshot[];
  has_history: boolean;
  message: string;
}

export interface PriceAlertRequest {
  product_id: string;
  product_title: string;
  product_url: string;
  retailer: string;
  target_price_inr: number;
  initial_price_inr?: number;
  current_price_inr?: number;
}

export interface PriceAlertResponse {
  id: number;
  product_id: string;
  product_title: string;
  retailer: string;
  target_price_inr: number;
  current_price_inr?: number;
  is_active: boolean;
  is_triggered: boolean;
  created_at: string;
  message: string;
}

export interface RetailerCoupon {
  id?: number;
  retailer: string;
  coupon_code: string;
  discount_text: string;
  terms?: string;
  expiry_date?: string;
  source: string;
  is_verified: boolean;
}

