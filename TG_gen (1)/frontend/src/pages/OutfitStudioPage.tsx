import React, { useState, useRef, useCallback, useMemo } from 'react';
import {
  OutfitGenerateRequest,
  OutfitGenerateResponse,
  GenerationStatus,
  ShoppingMatch,
} from '../types/outfit';
import { outfitStudioService } from '../services/api';
import { useAuth } from '../context/AuthContext';

import { OutfitInputForm } from '../components/OutfitStudio/OutfitInputForm';
import { OutfitConceptCard } from '../components/OutfitStudio/OutfitConceptCard';
import { OutfitItemCard } from '../components/OutfitStudio/OutfitItemCard';
import { ShoppingMatchCard } from '../components/OutfitStudio/ShoppingMatchCard';
import { ConceptVariationsGallery } from '../components/OutfitStudio/ConceptVariationsGallery';
import { RetailerSearchSection } from '../components/OutfitStudio/RetailerSearchSection';
import { GenerationStepper } from '../components/OutfitStudio/GenerationStepper';
import { ComparePricesSection } from '../components/OutfitStudio/ComparePricesSection';
import { CouponsSection } from '../components/OutfitStudio/CouponsSection';

import {
  Wand2,
  Bookmark,
  BookmarkCheck,
  RefreshCw,
  AlertTriangle,
  ShoppingBag,
  Info,
  Leaf,
  Sparkles,
  ArrowRight,
  Filter,
  Search,
  CheckCircle2,
  Eye,
  SlidersHorizontal,
} from 'lucide-react';

const STORE_FILTERS = [
  'All Stores',
  'Myntra',
  'AJIO',
  'Nykaa Fashion',
  'Amazon India',
  'Tata CLiQ',
  'Official Brand',
];

// ─────────────────────────────────────────────────────────────────────────────
// Empty state
// ─────────────────────────────────────────────────────────────────────────────
const EmptyState: React.FC = () => (
  <div className="flex flex-col items-center justify-center py-16 sm:py-20 text-center space-y-5 px-4 sm:px-6">
    <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-3xl bg-gradient-to-br from-forest-800 to-sage-700 flex items-center justify-center shadow-xl">
      <Wand2 className="w-10 h-10 sm:w-12 sm:h-12 text-cream-100" />
    </div>
    <div>
      <h3 className="text-xl sm:text-2xl font-bold text-charcoal-900 dark:text-cream-100">
        AI Outfit Studio
      </h3>
      <p className="mt-2 text-xs sm:text-sm text-charcoal-600 dark:text-charcoal-300 max-w-md leading-relaxed">
        Generate realistic sustainable dress and outfit concepts, browse 2–4 photorealistic visual variations, and explore verified shopping links for top Indian stores.
      </p>
    </div>
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 max-w-lg w-full text-left">
      {[
        { icon: '👗', text: 'Sage Green Tencel Midi Dress' },
        { icon: '💼', text: 'Formal Summer Office Look' },
        { icon: '🪡', text: 'Chanderi Festive Anarkali' },
        { icon: '👖', text: 'Weekend Organic Denim Kit' },
        { icon: '👔', text: 'Bamboo Lyocell Interview Set' },
        { icon: '🎒', text: 'Recycled Streetwear Capsule' },
      ].map((ex) => (
        <div
          key={ex.text}
          className="flex items-center gap-2 p-2.5 rounded-xl bg-cream-100/70 dark:bg-charcoal-800 border border-cream-200 dark:border-charcoal-700 text-xs text-charcoal-700 dark:text-charcoal-300"
        >
          <span className="text-base">{ex.icon}</span> <span className="truncate">{ex.text}</span>
        </div>
      ))}
    </div>
    <div className="flex items-center gap-1.5 text-xs text-charcoal-500 dark:text-charcoal-400">
      <ArrowRight className="w-3.5 h-3.5 text-forest-500" />
      Enter your occasion on the left and click <strong className="text-forest-700 dark:text-sage-300 ml-1">✨ Generate My Outfit</strong>
    </div>
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
// Error state
// ─────────────────────────────────────────────────────────────────────────────
const ErrorState: React.FC<{ message: string; onRetry: () => void }> = ({ message, onRetry }) => (
  <div className="flex flex-col items-center justify-center py-16 text-center space-y-4 px-6">
    <div className="w-16 h-16 rounded-2xl bg-rose-100 dark:bg-rose-950/60 flex items-center justify-center border border-rose-200 dark:border-rose-900">
      <AlertTriangle className="w-8 h-8 text-rose-500" />
    </div>
    <div>
      <h3 className="text-lg font-bold text-charcoal-900 dark:text-cream-100">Generation Failed</h3>
      <p className="mt-1 text-sm text-charcoal-600 dark:text-charcoal-400 max-w-sm">{message}</p>
    </div>
    <button
      onClick={onRetry}
      className="px-6 py-2.5 rounded-xl bg-forest-700 hover:bg-forest-600 text-cream-100 font-semibold text-sm transition flex items-center gap-2 shadow-sm"
    >
      <RefreshCw className="w-4 h-4" /> Try Again
    </button>
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
// Main Page Component
// ─────────────────────────────────────────────────────────────────────────────
export const OutfitStudioPage: React.FC = () => {
  const { user } = useAuth();
  const [status, setStatus] = useState<GenerationStatus>('idle');
  const [result, setResult] = useState<OutfitGenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isRegeneratingVar, setIsRegeneratingVar] = useState(false);
  const [selectedStoreFilter, setSelectedStoreFilter] = useState('All Stores');
  const [lastRequest, setLastRequest] = useState<OutfitGenerateRequest | null>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  // Progressive generation steps simulation
  const simulateSteps = useCallback(async () => {
    const steps: GenerationStatus[] = ['analyzing', 'styling', 'visualizing', 'shopping'];
    for (const step of steps) {
      setStatus(step);
      await new Promise((r) => setTimeout(r, 600));
    }
  }, []);

  const handleGenerate = useCallback(
    async (request: OutfitGenerateRequest) => {
      setStatus('analyzing');
      setError(null);
      setResult(null);
      setIsSaved(false);
      setLastRequest(request);
      setSelectedStoreFilter('All Stores');

      const stepPromise = simulateSteps();
      const apiPromise = outfitStudioService.generate(request);

      try {
        await stepPromise;
        const data = await apiPromise;
        setResult(data);
        setStatus('done');
        setTimeout(() => {
          resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || 'An unexpected error occurred.';
        setError(msg);
        setStatus('error');
      }
    },
    [simulateSteps]
  );

  const handleRegenerateVariation = async (variationIndex: number) => {
    if (!result || isRegeneratingVar) return;
    setIsRegeneratingVar(true);
    try {
      const res = await outfitStudioService.regenerateImage(result.generation_id, variationIndex);
      // Update state with new variation data
      setResult((prev) => {
        if (!prev) return prev;
        const updatedVars = prev.generated_images.map((v) =>
          v.variation_index === variationIndex
            ? {
                ...v,
                image_url: res.image_url,
                status: (res.status as any) || v.status,
                prompt: res.prompt || v.prompt,
              }
            : v
        );
        return {
          ...prev,
          generated_images: updatedVars,
          generated_image:
            variationIndex === 1
              ? {
                  ...prev.generated_image,
                  url: res.image_url,
                  status: (res.status as any) || prev.generated_image.status,
                }
              : prev.generated_image,
          generated_image_url: variationIndex === 1 ? res.image_url : prev.generated_image_url,
        };
      });
    } catch {
      // Keep existing
    } finally {
      setIsRegeneratingVar(false);
    }
  };

  const handleSave = async () => {
    if (!result || !user || isSaving) return;
    setIsSaving(true);
    try {
      await outfitStudioService.saveOutfit(result.generation_id);
      setIsSaved(true);
    } catch {
      // Silently handle
    } finally {
      setIsSaving(false);
    }
  };

  // Filter shopping results based on selected store chip
  const filteredProducts = useMemo(() => {
    if (!result) return [];
    const matches = result.shopping_results || result.shopping_matches || [];
    if (selectedStoreFilter === 'All Stores') return matches;
    return matches.filter(
      (m) =>
        m.retailer.toLowerCase().includes(selectedStoreFilter.toLowerCase()) ||
        selectedStoreFilter.toLowerCase().includes(m.retailer.toLowerCase())
    );
  }, [result, selectedStoreFilter]);

  const isLoading = ['analyzing', 'styling', 'visualizing', 'shopping'].includes(status);

  return (
    <div className="outfit-studio-page min-h-screen bg-cream-50 dark:bg-charcoal-950">
      <title>AI Outfit Studio – EcoFabric Indian Store Assistant</title>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Hero Section Header */}
        <div className="mb-6 sm:mb-8 rounded-3xl bg-gradient-to-br from-forest-950 via-charcoal-900 to-charcoal-950 border border-charcoal-800 p-6 sm:p-8 relative overflow-hidden shadow-lg">
          <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full bg-forest-700/10 blur-3xl pointer-events-none" />
          <div className="absolute -bottom-16 -left-16 w-60 h-60 rounded-full bg-sage-700/10 blur-3xl pointer-events-none" />

          <div className="relative flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-gradient-to-br from-forest-500 to-sage-600 flex items-center justify-center shadow-xl flex-shrink-0">
                <Wand2 className="w-6 h-6 sm:w-7 sm:h-7 text-cream-100" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-cream-50 tracking-tight">
                  AI Outfit Studio
                </h1>
                <p className="text-xs sm:text-sm text-charcoal-400 mt-1">
                  Realistic dress concepts, AI visual variations & verified shopping across Myntra, AJIO, Nykaa Fashion & Amazon India
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-charcoal-800/80 text-sage-300 border border-charcoal-700">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Multi-Variation Concepts
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-charcoal-800/80 text-forest-300 border border-charcoal-700">
                <Leaf className="w-3.5 h-3.5 text-forest-400" /> Indian Eco Fabrics
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-charcoal-800/80 text-amber-300 border border-charcoal-700">
                <ShoppingBag className="w-3.5 h-3.5 text-amber-400" /> Real Store Links
              </span>
            </div>
          </div>
        </div>

        {/* 2-Column Responsive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
          {/* ── LEFT COLUMN: Input Form + Concept Overview + Garment Breakdown + Coupons ── */}
          <div className="lg:col-span-5 xl:col-span-5 space-y-6">
            {/* Design Look Input Form */}
            <div className="rounded-3xl bg-white dark:bg-charcoal-900 border border-cream-200 dark:border-charcoal-800 shadow-sm p-5 sm:p-6">
              <h2 className="text-base sm:text-lg font-bold text-charcoal-900 dark:text-cream-100 mb-4 flex items-center gap-2">
                <Wand2 className="w-4 h-4 text-forest-600" /> Design & Refine Look
              </h2>
              <OutfitInputForm onGenerate={handleGenerate} isLoading={isLoading} />
            </div>

            {/* When Done: Move Outfit Concept & Garment Breakdown to Left Column */}
            {status === 'done' && result && (
              <>
                {/* ── Concept Overview Card ── */}
                <div className="animate-fadeSlideUp">
                  <OutfitConceptCard
                    outfit={result.outfit}
                    isMockMode={result.is_mock_mode}
                    generatedImageUrl={result.generated_image_url}
                  />
                </div>

                {/* ── Garment Item Breakdown ── */}
                <section className="rounded-3xl bg-charcoal-900 border border-charcoal-800 shadow-xl p-5 sm:p-6 animate-fadeSlideUp">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm sm:text-base font-extrabold text-cream-50 flex items-center gap-2 uppercase tracking-wide">
                      🛍️ Garment Breakdown
                    </h3>
                    <span className="text-xs font-bold text-sage-300">
                      {result.outfit.items.length} garments
                    </span>
                  </div>

                  <div className="grid grid-cols-1 gap-3 sm:gap-4">
                    {result.outfit.items.map((item, i) => (
                      <OutfitItemCard key={item.id || i} item={item} index={i} />
                    ))}
                  </div>

                  {result.outfit.total_estimated_price_inr != null && (
                    <div className="mt-4 p-4 rounded-2xl bg-forest-950/80 border border-forest-800 flex items-center justify-between">
                      <span className="text-xs sm:text-sm font-semibold text-cream-200">
                        Total Estimated Look Cost
                      </span>
                      <span className="text-base sm:text-lg font-black text-emerald-400">
                        ₹{result.outfit.total_estimated_price_inr.toLocaleString('en-IN')}
                      </span>
                    </div>
                  )}
                </section>

                {/* ── Active Indian Store Coupons ── */}
                <div className="animate-fadeSlideUp">
                  <CouponsSection retailerFilter={selectedStoreFilter !== 'All Stores' ? selectedStoreFilter : undefined} />
                </div>
              </>
            )}
          </div>

          {/* ── RIGHT COLUMN: Visual Variations + Price Comparison + Store Search ── */}
          <div className="lg:col-span-7 xl:col-span-7 space-y-6" ref={resultRef}>
            {/* Loading State with Stepper */}
            {isLoading && (
              <div className="rounded-3xl bg-white dark:bg-charcoal-900 border border-cream-200 dark:border-charcoal-800 shadow-sm p-6 sm:p-8 space-y-6">
                <div className="text-center">
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-forest-50 dark:bg-forest-950/50 border border-forest-200 dark:border-forest-800 text-forest-700 dark:text-forest-300 text-xs sm:text-sm font-semibold">
                    <Sparkles className="w-4 h-4 animate-pulse text-amber-400" />
                    Generating your sustainable outfit concept & visual variations…
                  </div>
                </div>
                <GenerationStepper status={status} />
                <div className="space-y-3 pt-2">
                  <div className="h-28 rounded-2xl bg-cream-100 dark:bg-charcoal-800 animate-pulse" />
                  <div className="h-64 rounded-2xl bg-cream-100 dark:bg-charcoal-800 animate-pulse" />
                </div>
              </div>
            )}

            {/* Error State */}
            {status === 'error' && error && (
              <div className="rounded-3xl bg-white dark:bg-charcoal-900 border border-rose-200 dark:border-rose-900 shadow-sm overflow-hidden">
                <ErrorState message={error} onRetry={() => lastRequest && handleGenerate(lastRequest)} />
              </div>
            )}

            {/* Empty State */}
            {status === 'idle' && (
              <div className="rounded-3xl bg-white dark:bg-charcoal-900 border border-cream-200 dark:border-charcoal-800 shadow-sm overflow-hidden">
                <EmptyState />
              </div>
            )}

            {/* ── DONE RESULT SECTION (RIGHT SIDE) ── */}
            {status === 'done' && result && (
              <div className="space-y-6">
                {/* ── SECTION 1: Concept Visualizations & Variations ────── */}
                <div className="animate-fadeSlideUp">
                  <ConceptVariationsGallery
                    primaryImage={result.generated_image}
                    variations={result.generated_images}
                    outfitName={result.outfit.outfit_name}
                    onRegenerateVariation={handleRegenerateVariation}
                    isRegenerating={isRegeneratingVar}
                  />
                </div>

                {/* ── SECTION 2: Compare Prices & Buy Similar Styles ─────── */}
                <div className="animate-fadeSlideUp">
                  <ComparePricesSection
                    outfit={result.outfit}
                    genderPreference={lastRequest?.gender_preference || (result as any)?.gender_preference}
                    budgetInr={result.outfit.total_estimated_price_inr || undefined}
                    initialFallbackLinks={result.retailer_search_links}
                    isDemoMode={result.is_mock_mode}
                  />
                </div>

                {/* ── SECTION 3: Direct Indian Retailer Search Links ─────── */}
                <div className="animate-fadeSlideUp">
                  <RetailerSearchSection
                    searchLinks={result.retailer_search_links}
                    outfitName={result.outfit.outfit_name}
                    storeVerificationNotice={result.store_verification_notice || 'Prices and details verified on retailer store.'}
                  />
                </div>

                {/* Consumer Disclaimer */}
                <div className="p-4 rounded-2xl bg-cream-100/60 dark:bg-charcoal-800/80 border border-cream-200 dark:border-charcoal-700">
                  <p className="text-[11px] text-charcoal-600 dark:text-charcoal-400 leading-relaxed">
                    <strong>Consumer Notice:</strong> {result.disclaimer}
                  </p>
                </div>

                {/* Engine Footnote */}
                <div className="text-center py-2">
                  <p className="text-[11px] text-charcoal-400 dark:text-charcoal-600">
                    Provider Engine: LLM/{result.provider_info.llm || 'mock'} · Image/{result.provider_info.image || 'mock'} · Shopping/{result.provider_info.shopping || 'mock'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};
