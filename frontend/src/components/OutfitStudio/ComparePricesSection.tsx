import React, { useState, useEffect, useCallback } from 'react';
import {
  Outfit,
  OutfitItem,
  ProductResult,
  BestDealInfo,
  PriceComparisonResponse,
  RetailerSearchLink,
  getItemCategoryIcon,
} from '../../types/outfit';
import { outfitStudioService } from '../../services/api';
import { ShoppingMatchCard } from './ShoppingMatchCard';
import { CouponsSection } from './CouponsSection';
import {
  ShoppingBag,
  TrendingDown,
  Leaf,
  Sparkles,
  ShieldCheck,
  Filter,
  ExternalLink,
  Search,
  AlertTriangle,
  RefreshCw,
  Tag,
  ArrowRight,
  BadgePercent,
  CheckCircle2,
  Info,
} from 'lucide-react';

interface ComparePricesSectionProps {
  outfit: Outfit;
  genderPreference?: string;
  style?: string;
  budgetInr?: number;
  initialProducts?: ProductResult[];
  initialFallbackLinks?: RetailerSearchLink[];
  isDemoMode?: boolean;
}

const STORE_FILTERS = [
  'All Stores',
  'Myntra',
  'AJIO',
  'Nykaa Fashion',
  'Tata CLiQ',
  'Amazon India',
  'Flipkart',
  'Official Brands',
];

export const ComparePricesSection: React.FC<ComparePricesSectionProps> = ({
  outfit,
  genderPreference,
  style,
  budgetInr,
  initialProducts,
  initialFallbackLinks,
  isDemoMode = false,
}) => {
  const items = outfit.items || [];
  const [selectedItemIndex, setSelectedItemIndex] = useState<number>(0);
  const [selectedStore, setSelectedStore] = useState<string>('All Stores');
  const [onlyBudgetFriendly, setOnlyBudgetFriendly] = useState<boolean>(false);
  const [sortByPrice, setSortByPrice] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [comparisonData, setComparisonData] = useState<PriceComparisonResponse | null>(null);

  const currentOutfitItem: OutfitItem | undefined = items[selectedItemIndex] || items[0];

  // Fetch comparison data for the selected outfit item
  const loadComparison = useCallback(async (item: OutfitItem, store: string, budgetFriendly: boolean) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await outfitStudioService.searchProducts({
        outfit_item_name: item.name,
        category: item.category,
        color: item.color,
        fabric: item.recommended_fabric || item.preferred_fabric,
        gender: genderPreference,
        style: style,
        occasion: outfit.occasion,
        budget_inr: item.estimated_budget_inr || budgetInr,
        is_budget_friendly: budgetFriendly,
        retailer_filter: store,
        limit: 12,
      });
      setComparisonData(res);
    } catch (err: any) {
      setError('Unable to load real store products for this item.');
    } finally {
      setIsLoading(false);
    }
  }, [genderPreference, style, outfit.occasion, budgetInr]);

  useEffect(() => {
    if (currentOutfitItem) {
      loadComparison(currentOutfitItem, selectedStore, onlyBudgetFriendly);
    }
  }, [selectedItemIndex, selectedStore, onlyBudgetFriendly, loadComparison]);

  const products = comparisonData?.products || initialProducts || [];
  const bestDeal: BestDealInfo | null | undefined = comparisonData?.best_deal;
  const fallbackLinks = comparisonData?.retailer_fallback_links || initialFallbackLinks || [];
  const demoActive = isDemoMode || comparisonData?.is_demo_mode;

  // Filtered by store tab & budget-friendly filter
  let filteredProducts = products.filter((p) => {
    const storeMatch =
      selectedStore === 'All Stores' ||
      p.retailer.toLowerCase().includes(selectedStore.toLowerCase()) ||
      selectedStore.toLowerCase().includes(p.retailer.toLowerCase());

    if (!storeMatch) return false;

    if (onlyBudgetFriendly) {
      const price = p.current_price_inr ?? 999999;
      return price <= 2500 || (p.discount_percent && p.discount_percent >= 30);
    }
    return true;
  });

  if (sortByPrice) {
    filteredProducts = [...filteredProducts].sort(
      (a, b) => (a.current_price_inr ?? 999999) - (b.current_price_inr ?? 999999)
    );
  }

  return (
    <section className="rounded-3xl bg-white dark:bg-charcoal-900 border border-cream-200 dark:border-charcoal-800 shadow-sm p-5 sm:p-7 space-y-6 animate-fadeSlideUp">
      {/* ── Section Header ────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-cream-200 dark:border-charcoal-800 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-forest-600 to-sage-600 text-cream-100 flex items-center justify-center shadow-md flex-shrink-0">
            <ShoppingBag className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg sm:text-xl font-extrabold text-forest-950 dark:text-cream-50 tracking-tight">
                Compare Prices & Buy Similar Styles
              </h3>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-forest-50 dark:bg-forest-950/60 text-forest-700 dark:text-sage-300 border border-forest-200 dark:border-forest-800">
                India Stores
              </span>
            </div>
            <p className="text-xs sm:text-sm font-medium text-forest-900 dark:text-cream-200 mt-0.5">
              Live matching styles across Myntra, AJIO, Nykaa Fashion, Tata CLiQ, Amazon India & Flipkart.
            </p>
          </div>
        </div>

        {demoActive ? (
          <div className="px-3.5 py-1.5 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-xs font-semibold flex items-center gap-1.5 self-start sm:self-auto">
            <Info className="w-4 h-4 text-amber-500" />
            <span>Demo Mode — product prices and availability are sample data.</span>
          </div>
        ) : (
          <div className="px-3.5 py-1.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs font-semibold flex items-center gap-1.5 self-start sm:self-auto">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>Verified Live Feed Comparison</span>
          </div>
        )}
      </div>

      {/* ── Item Selection Chips (Extracted Outfit Items) ─────────────────── */}
      {items.length > 0 && (
        <div className="space-y-2">
          <label className="block text-xs font-bold text-forest-900 dark:text-cream-200 uppercase tracking-wider">
            Select Outfit Piece to Compare:
          </label>
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            {items.map((item, idx) => {
              const isSelected = idx === selectedItemIndex;
              return (
                <button
                  key={item.id || idx}
                  type="button"
                  onClick={() => setSelectedItemIndex(idx)}
                  className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all duration-200 flex items-center gap-2 whitespace-nowrap border shadow-sm ${
                    isSelected
                      ? 'bg-forest-700 text-cream-100 border-forest-600 shadow-md ring-2 ring-forest-400/30'
                      : 'bg-cream-100/70 dark:bg-charcoal-800 text-charcoal-800 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-forest-400'
                  }`}
                >
                  <span className="text-sm">
                    {getItemCategoryIcon(item.category, item.name, genderPreference)}
                  </span>
                  <span>{item.name}</span>
                  {item.estimated_budget_inr && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${isSelected ? 'bg-forest-800/80 text-cream-100' : 'bg-cream-200 dark:bg-charcoal-700 text-charcoal-600 dark:text-charcoal-300'}`}>
                      ₹{item.estimated_budget_inr.toLocaleString('en-IN')}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ── BEST DEAL CARD BANNER ───────────────────────────────────────── */}
      {bestDeal && (bestDeal.best_price_product || bestDeal.best_sustainable_product) && (
        <div className="rounded-3xl bg-gradient-to-br from-forest-950 via-charcoal-900 to-forest-900 border border-forest-800/80 p-5 sm:p-6 text-cream-50 relative overflow-hidden shadow-xl">
          <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-forest-500/10 blur-2xl pointer-events-none" />

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-forest-800/60 pb-4 mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-amber-400/20 text-amber-300 flex items-center justify-center border border-amber-400/30">
                <BadgePercent className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-base font-extrabold text-cream-50 flex items-center gap-2">
                  Best Deal Comparison Summary <Sparkles className="w-4 h-4 text-amber-400" />
                </h4>
                <p className="text-xs text-charcoal-300">
                  AI-evaluated top value and sustainable choices for this outfit item
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-forest-900/90 text-sage-200 border border-forest-700">
                {bestDeal.verified_source_label}
              </span>
            </div>
          </div>

          {/* Dual Deal Cards: Best Price vs Best Sustainable */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 1. Best Price Pick */}
            {bestDeal.best_price_product && (
              <div className="p-4 rounded-2xl bg-charcoal-900/80 border border-forest-700/60 flex items-start gap-3.5 backdrop-blur-sm">
                <div className="w-16 h-20 rounded-xl bg-charcoal-800 overflow-hidden flex-shrink-0 border border-white/10">
                  {bestDeal.best_price_product.image_url ? (
                    <img
                      src={bestDeal.best_price_product.image_url}
                      alt={bestDeal.best_price_product.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-charcoal-400">
                      ₹
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                      <TrendingDown className="w-3 h-3" /> Best Price
                    </span>
                    <span className="text-[11px] font-bold text-amber-300">
                      {bestDeal.best_price_product.retailer}
                    </span>
                  </div>

                  <p className="text-xs font-bold text-cream-100 truncate mt-1">
                    {bestDeal.best_price_product.title}
                  </p>

                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-base font-black text-emerald-400">
                      ₹{bestDeal.best_price_product.current_price_inr?.toLocaleString('en-IN')}
                    </span>
                    {bestDeal.estimated_savings_inr && bestDeal.estimated_savings_inr > 0 && (
                      <span className="text-[11px] text-amber-300 font-semibold">
                        (Save ₹{bestDeal.estimated_savings_inr.toLocaleString('en-IN')})
                      </span>
                    )}
                  </div>

                  <a
                    href={bestDeal.best_price_product.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-flex items-center gap-1 text-[11px] font-bold text-sage-300 hover:text-cream-100 hover:underline"
                  >
                    <span>View Deal on {bestDeal.best_price_product.retailer}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            )}

            {/* 2. Best Sustainable Pick */}
            {bestDeal.best_sustainable_product && (
              <div className="p-4 rounded-2xl bg-charcoal-900/80 border border-forest-700/60 flex items-start gap-3.5 backdrop-blur-sm">
                <div className="w-16 h-20 rounded-xl bg-charcoal-800 overflow-hidden flex-shrink-0 border border-white/10">
                  {bestDeal.best_sustainable_product.image_url ? (
                    <img
                      src={bestDeal.best_sustainable_product.image_url}
                      alt={bestDeal.best_sustainable_product.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-charcoal-400">
                      🌿
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-forest-500/30 text-sage-200 border border-forest-400/40 flex items-center gap-1">
                      <Leaf className="w-3 h-3 text-forest-300" /> Best Eco Option
                    </span>
                    <span className="text-[11px] font-bold text-sage-300">
                      {bestDeal.best_sustainable_product.retailer}
                    </span>
                  </div>

                  <p className="text-xs font-bold text-cream-100 truncate mt-1">
                    {bestDeal.best_sustainable_product.title}
                  </p>

                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-base font-black text-sage-300">
                      ₹{bestDeal.best_sustainable_product.current_price_inr?.toLocaleString('en-IN')}
                    </span>
                    {bestDeal.best_sustainable_product.fabric_details && (
                      <span className="text-[10px] text-charcoal-300 truncate">
                        · {bestDeal.best_sustainable_product.fabric_details}
                      </span>
                    )}
                  </div>

                  <a
                    href={bestDeal.best_sustainable_product.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-flex items-center gap-1 text-[11px] font-bold text-sage-300 hover:text-cream-100 hover:underline"
                  >
                    <span>View on {bestDeal.best_sustainable_product.retailer}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── STORE TABS / FILTERS & BUDGET FILTER ───────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 py-2 border-b border-cream-200 dark:border-charcoal-800">
        <div className="flex items-center gap-2 overflow-x-auto">
          <span className="text-xs font-bold text-charcoal-500 dark:text-charcoal-400 flex items-center gap-1.5 flex-shrink-0 mr-1">
            <Filter className="w-3.5 h-3.5 text-forest-600" /> Store:
          </span>
          {STORE_FILTERS.map((store) => {
            const isActive = selectedStore === store;
            return (
              <button
                key={store}
                type="button"
                onClick={() => setSelectedStore(store)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap border shadow-sm ${
                  isActive
                    ? 'bg-forest-700 text-cream-100 border-forest-600 ring-2 ring-forest-400/20'
                    : 'bg-cream-100/70 dark:bg-charcoal-800 text-charcoal-700 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-forest-400'
                }`}
              >
                {store}
              </button>
            );
          })}
        </div>

        {/* Budget-friendly & Sort Quick Toggles */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            type="button"
            onClick={() => setOnlyBudgetFriendly(v => !v)}
            className={`px-3 py-1.5 rounded-full text-xs font-bold transition flex items-center gap-1.5 border shadow-sm ${
              onlyBudgetFriendly
                ? 'bg-emerald-600 text-white border-emerald-500 ring-2 ring-emerald-400/30'
                : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800 hover:bg-emerald-100'
            }`}
          >
            <span>💰 Budget-Friendly &lt; ₹2.5k</span>
            {onlyBudgetFriendly && <span className="text-[10px] ml-0.5">✓</span>}
          </button>

          <button
            type="button"
            onClick={() => setSortByPrice(v => !v)}
            className={`px-3 py-1.5 rounded-full text-xs font-bold transition flex items-center gap-1 border shadow-sm ${
              sortByPrice
                ? 'bg-charcoal-800 text-cream-100 border-charcoal-700'
                : 'bg-cream-100 dark:bg-charcoal-800 text-charcoal-700 dark:text-cream-300 border-cream-200 dark:border-charcoal-700 hover:border-forest-400'
            }`}
          >
            <span>{sortByPrice ? '💸 Price: Low to High ✓' : '↕ Sort by Price'}</span>
          </button>
        </div>
      </div>

      {/* ── PRODUCT CARDS GRID ─────────────────────────────────────────── */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 py-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-80 rounded-3xl bg-cream-100 dark:bg-charcoal-800 animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="p-8 text-center rounded-3xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 space-y-3">
          <AlertTriangle className="w-8 h-8 text-rose-500 mx-auto" />
          <p className="text-sm font-bold text-charcoal-900 dark:text-cream-100">{error}</p>
          <button
            onClick={() => currentOutfitItem && loadComparison(currentOutfitItem, selectedStore, onlyBudgetFriendly)}
            className="px-4 py-2 rounded-xl bg-forest-700 text-cream-100 text-xs font-bold hover:bg-forest-600 transition inline-flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry Product Search
          </button>
        </div>
      ) : filteredProducts.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredProducts.map((prod) => (
            <ShoppingMatchCard key={prod.id} match={prod} />
          ))}
        </div>
      ) : (
        <div className="py-12 text-center rounded-3xl bg-cream-50 dark:bg-charcoal-800/40 border border-cream-200 dark:border-charcoal-700 p-8 space-y-3">
          <ShoppingBag className="w-10 h-10 text-charcoal-400 mx-auto" />
          <h4 className="text-base font-bold text-charcoal-900 dark:text-cream-100">
            No direct matching products found on {selectedStore}
          </h4>
          <p className="text-xs text-charcoal-600 dark:text-charcoal-400 max-w-md mx-auto">
            Try switching the store filter or use the direct verified search button below to browse this style live.
          </p>
          <button
            onClick={() => setSelectedStore('All Stores')}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-forest-700 text-cream-100 hover:bg-forest-600 transition"
          >
            Show All Stores
          </button>
        </div>
      )}

      {/* ── VERIFIED COUPONS SECTION ───────────────────────────────────── */}
      <CouponsSection retailerFilter={selectedStore === 'All Stores' ? undefined : selectedStore} />

      {/* ── RETAILER SEARCH FALLBACK BUTTONS ────────────────────────────── */}
      <div className="rounded-3xl bg-cream-100/60 dark:bg-charcoal-800/60 border border-cream-200 dark:border-charcoal-700 p-5 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h4 className="text-sm font-bold text-charcoal-900 dark:text-cream-100 flex items-center gap-2">
              <Search className="w-4 h-4 text-forest-600" /> Search Directly on Indian Stores
            </h4>
            <p className="text-xs text-charcoal-500 dark:text-charcoal-400 mt-0.5">
              Retailer Search — verify price and availability directly on the store website.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
          {fallbackLinks.map((link) => (
            <a
              key={link.retailer}
              href={link.search_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-2xl bg-white dark:bg-charcoal-800 border border-cream-200 dark:border-charcoal-700 hover:border-forest-500 hover:shadow-md transition flex items-center justify-between text-xs font-bold text-charcoal-800 dark:text-cream-100 group"
            >
              <span className="flex items-center gap-2 truncate">
                <span>{link.icon || '🛍️'}</span>
                <span className="truncate">{link.retailer}</span>
              </span>
              <ExternalLink className="w-3.5 h-3.5 text-charcoal-400 group-hover:text-forest-600 transition-colors flex-shrink-0" />
            </a>
          ))}
        </div>
      </div>
    </section>
  );
};
