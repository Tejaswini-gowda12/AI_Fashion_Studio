import React, { useState } from 'react';
import { ProductResult, ShoppingMatch, RETAILER_BADGES } from '../../types/outfit';
import { outfitStudioService } from '../../services/api';
import { PriceHistoryModal } from './PriceHistoryModal';
import { PriceAlertModal } from './PriceAlertModal';
import {
  ExternalLink,
  Leaf,
  ShoppingBag,
  AlertCircle,
  ImageOff,
  Clock,
  ShieldCheck,
  Bookmark,
  BookmarkCheck,
  BellRing,
  LineChart,
  Tag,
} from 'lucide-react';

interface ShoppingMatchCardProps {
  match: ProductResult | ShoppingMatch;
  onSave?: (product: any) => void;
}

export const ShoppingMatchCard: React.FC<ShoppingMatchCardProps> = ({ match, onSave }) => {
  const [imgError, setImgError] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [showAlertModal, setShowAlertModal] = useState(false);

  const retailerBadge = RETAILER_BADGES[match.retailer] || {
    label: match.retailer || 'Retail Store',
    bg: 'bg-forest-50 dark:bg-forest-950/40',
    text: 'text-forest-700 dark:text-forest-300',
    border: 'border-forest-200 dark:border-forest-800',
  };

  const isVerified = match.status === 'verified';
  const currPrice = (match as ProductResult).current_price_inr ?? (match as ShoppingMatch).price_inr ?? (match as ShoppingMatch).price;
  const origPrice = (match as ProductResult).original_price_inr;
  const discountPct = (match as ProductResult).discount_percent;

  const lastUpdated = (match as ProductResult).last_updated_at || (match as ShoppingMatch).timestamp;
  const formattedTime = lastUpdated
    ? new Date(lastUpdated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : null;

  const fabricText = match.fabric_details;
  const sustainabilityText =
    (match as ProductResult).sustainability_details || (match as ShoppingMatch).sustainability_label;

  const handleSave = async () => {
    if (isSaving || isSaved) return;
    setIsSaving(true);
    try {
      if ((match as ProductResult).id) {
        await outfitStudioService.saveProduct(match as ProductResult);
      }
      setIsSaved(true);
      if (onSave) onSave(match);
    } catch {
      // Local toggle fallback
      setIsSaved(true);
    } finally {
      setIsSaving(false);
    }
  };

  const prodId = String(match.id || match.title.replace(/\s+/g, '-').toLowerCase());

  return (
    <>
      <div className="group flex flex-col rounded-3xl border border-cream-200 dark:border-charcoal-700 bg-white dark:bg-charcoal-900 overflow-hidden hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
        {/* Product Image Stage */}
        <div className="relative w-full aspect-[4/5] bg-cream-100 dark:bg-charcoal-800 overflow-hidden">
          {match.image_url && !imgError ? (
            <img
              src={match.image_url}
              alt={match.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center gap-2 text-charcoal-400">
              <ImageOff className="w-10 h-10 opacity-40" />
              <span className="text-xs font-medium">Product Image</span>
            </div>
          )}

          {/* Retailer badge at top left */}
          <div
            className={`absolute top-3 left-3 px-3 py-1 rounded-full text-xs font-bold backdrop-blur-md border shadow-sm ${retailerBadge.bg} ${retailerBadge.text} ${retailerBadge.border}`}
          >
            {match.retailer}
          </div>

          {/* Match score at top right */}
          <div className="absolute top-3 right-3 flex items-center gap-1.5">
            <div className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-charcoal-950/85 text-cream-100 backdrop-blur-sm shadow-sm border border-white/10">
              {Math.round(match.match_score * 100)}% match
            </div>
          </div>

          {/* Discount & Budget Badges */}
          <div className="absolute bottom-3 left-3 flex items-center gap-1.5">
            {discountPct && discountPct > 0 && (
              <div className="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-rose-600 text-cream-100 shadow-md flex items-center gap-1">
                <Tag className="w-3 h-3" />
                <span>{Math.round(discountPct)}% OFF</span>
              </div>
            )}
            {currPrice != null && Number(currPrice) <= 2200 && (
              <div className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-600/90 text-white shadow-md backdrop-blur-sm flex items-center gap-1">
                <span>💰 Budget Pick</span>
              </div>
            )}
          </div>

          {/* Verification status label badge */}
          <div className="absolute bottom-3 right-3">
            {isVerified ? (
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-950/90 text-emerald-300 border border-emerald-500/40 backdrop-blur-sm flex items-center gap-1 shadow-sm">
                <ShieldCheck className="w-3 h-3 text-emerald-400" /> Verified
              </span>
            ) : (
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-950/90 text-amber-300 border border-amber-500/40 backdrop-blur-sm">
                Demo
              </span>
            )}
          </div>
        </div>

        {/* Product Details Body */}
        <div className="flex flex-col flex-1 p-4 sm:p-5 gap-3 bg-white dark:bg-charcoal-900 text-charcoal-900 dark:text-cream-100">
          {/* Title and Retailer Info */}
          <div>
            <p className="text-sm sm:text-base font-bold text-forest-950 dark:text-cream-50 leading-snug line-clamp-2">
              {match.title}
            </p>
            <p className="text-xs text-forest-800 dark:text-cream-300 mt-1 flex items-center gap-1.5">
              Available at <strong className="text-forest-950 dark:text-cream-200">{match.retailer}</strong>
            </p>
          </div>

          {/* Price Block: Current + Original Price */}
          <div className="flex items-baseline justify-between pt-1 border-t border-cream-100 dark:border-charcoal-800">
            <div className="flex items-baseline gap-2">
              {currPrice != null ? (
                <>
                  <span className="text-xl sm:text-2xl font-black text-forest-900 dark:text-sage-300">
                    ₹{Number(currPrice).toLocaleString('en-IN')}
                  </span>
                  {origPrice && origPrice > currPrice && (
                    <span className="text-xs text-charcoal-400 line-through">
                      ₹{Number(origPrice).toLocaleString('en-IN')}
                    </span>
                  )}
                </>
              ) : (
                <span className="text-xs text-forest-800 italic">Check price on store</span>
              )}
            </div>

            {formattedTime && (
              <span className="text-[10px] text-forest-700 dark:text-charcoal-400 flex items-center gap-1">
                <Clock className="w-3 h-3 text-forest-600 dark:text-charcoal-400" />
                {formattedTime}
              </span>
            )}
          </div>

          {/* Fabric Details (only if provided by retailer) */}
          {fabricText && (
            <div className="p-2.5 rounded-2xl bg-forest-50/70 dark:bg-charcoal-800/80 border border-forest-100 dark:border-charcoal-700 text-xs text-forest-950 dark:text-sage-200 leading-tight">
              <strong className="text-forest-900 dark:text-sage-400">Fabric:</strong> {fabricText}
            </div>
          )}

          {/* Sustainability Label */}
          {sustainabilityText && (
            <div className="flex items-center gap-1.5 text-xs text-forest-700 dark:text-forest-400 font-semibold">
              <Leaf className="w-3.5 h-3.5 text-forest-600 dark:text-forest-400 flex-shrink-0" />
              <span className="line-clamp-1">{sustainabilityText}</span>
            </div>
          )}

          <div className="flex-1 min-h-[6px]" />

          {/* Quick Actions Row: Price History & Price Alert */}
          <div className="grid grid-cols-2 gap-2 pt-1">
            <button
              type="button"
              onClick={() => setShowHistoryModal(true)}
              className="px-2.5 py-1.5 rounded-xl text-[11px] font-semibold bg-cream-100/80 hover:bg-cream-200 dark:bg-charcoal-800 dark:hover:bg-charcoal-700 text-charcoal-700 dark:text-cream-200 border border-cream-200 dark:border-charcoal-700 transition flex items-center justify-center gap-1"
            >
              <LineChart className="w-3 h-3 text-forest-600 dark:text-sage-400" />
              <span>Price History</span>
            </button>

            <button
              type="button"
              onClick={() => setShowAlertModal(true)}
              className="px-2.5 py-1.5 rounded-xl text-[11px] font-semibold bg-cream-100/80 hover:bg-cream-200 dark:bg-charcoal-800 dark:hover:bg-charcoal-700 text-charcoal-700 dark:text-cream-200 border border-cream-200 dark:border-charcoal-700 transition flex items-center justify-center gap-1"
            >
              <BellRing className="w-3 h-3 text-amber-500" />
              <span>Set Alert</span>
            </button>
          </div>

          {/* Primary Action Row: "Buy Now" + "Save Product" */}
          <div className="flex items-center gap-2 pt-1">
            <a
              id={`buy-now-${prodId}`}
              href={match.product_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl text-xs sm:text-sm font-bold bg-forest-700 hover:bg-forest-600 text-cream-100 shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer"
            >
              <ShoppingBag className="w-4 h-4" />
              <span>Buy Now on {match.retailer}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>

            <button
              type="button"
              onClick={handleSave}
              disabled={isSaved || isSaving}
              title={isSaved ? 'Saved to Profile' : 'Save Product'}
              className={`p-3 rounded-2xl border transition ${
                isSaved
                  ? 'bg-forest-100 dark:bg-forest-950/60 text-forest-700 dark:text-forest-300 border-forest-300 dark:border-forest-700'
                  : 'bg-cream-100 dark:bg-charcoal-800 text-charcoal-700 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-forest-500'
              }`}
            >
              {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
            </button>
          </div>

          {/* Notice footnote */}
          <p className="text-[9px] text-charcoal-400 text-center leading-tight flex items-center justify-center gap-1">
            <AlertCircle className="w-2.5 h-2.5 flex-shrink-0 text-charcoal-400" />
            <span>Verify price & availability on store website</span>
          </p>
        </div>
      </div>

      {/* Modals */}
      <PriceHistoryModal
        productId={prodId}
        productTitle={match.title}
        retailer={match.retailer}
        currentPriceInr={currPrice}
        isOpen={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
      />

      <PriceAlertModal
        productId={prodId}
        productTitle={match.title}
        productUrl={match.product_url}
        retailer={match.retailer}
        currentPriceInr={currPrice}
        isOpen={showAlertModal}
        onClose={() => setShowAlertModal(false)}
      />
    </>
  );
};
