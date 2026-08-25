import React, { useEffect, useState } from 'react';
import { PriceHistoryResponse } from '../../types/outfit';
import { outfitStudioService } from '../../services/api';
import {
  X,
  TrendingDown,
  TrendingUp,
  Clock,
  ShieldCheck,
  AlertCircle,
  Calendar,
  IndianRupee,
} from 'lucide-react';

interface PriceHistoryModalProps {
  productId: string;
  productTitle: string;
  retailer: string;
  currentPriceInr?: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export const PriceHistoryModal: React.FC<PriceHistoryModalProps> = ({
  productId,
  productTitle,
  retailer,
  currentPriceInr,
  isOpen,
  onClose,
}) => {
  const [data, setData] = useState<PriceHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && productId) {
      setIsLoading(true);
      outfitStudioService
        .getPriceHistory(productId, currentPriceInr, retailer)
        .then((res) => setData(res))
        .catch(() => {
          setData({
            product_id: productId,
            retailer,
            current_price_inr: currentPriceInr,
            lowest_price_inr: currentPriceInr,
            highest_price_inr: currentPriceInr,
            snapshots: [],
            has_history: false,
            message: 'Price history will appear after we collect verified price updates.',
          });
        })
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, productId, currentPriceInr, retailer]);

  if (!isOpen) return null;

  const snapshots = data?.snapshots || [];
  const minPrice = data?.lowest_price_inr ?? currentPriceInr ?? 0;
  const maxPrice = data?.highest_price_inr ?? currentPriceInr ?? 0;
  const currPrice = data?.current_price_inr ?? currentPriceInr ?? 0;

  // Simple SVG sparkline calculations
  const priceRange = maxPrice - minPrice || 1;
  const chartHeight = 120;
  const chartWidth = 400;
  const points = snapshots.map((s, idx) => {
    const x = snapshots.length > 1 ? (idx / (snapshots.length - 1)) * (chartWidth - 40) + 20 : chartWidth / 2;
    const y = chartHeight - ((s.price_inr - minPrice) / priceRange) * (chartHeight - 40) - 20;
    return { x, y, price: s.price_inr, date: s.recorded_at };
  });

  const pathD = points.length > 1
    ? `M ${points.map((p) => `${p.x},${p.y}`).join(' L ')}`
    : '';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-lg rounded-3xl bg-white dark:bg-charcoal-900 border border-cream-200 dark:border-charcoal-700 shadow-2xl p-6 overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 border-b border-cream-200 dark:border-charcoal-800 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-forest-50 dark:bg-forest-950/60 text-forest-700 dark:text-sage-300 border border-forest-200 dark:border-forest-800">
                {retailer}
              </span>
              <span className="text-xs font-semibold text-charcoal-500 dark:text-charcoal-400">
                Price History
              </span>
            </div>
            <h3 className="text-base font-bold text-charcoal-900 dark:text-cream-100 mt-1 line-clamp-1">
              {productTitle}
            </h3>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-charcoal-400 hover:text-charcoal-700 dark:hover:text-cream-100 hover:bg-cream-100 dark:hover:bg-charcoal-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-forest-600 border-t-transparent animate-spin" />
            <p className="text-xs text-charcoal-500 dark:text-charcoal-400">Loading verified price snapshots…</p>
          </div>
        ) : (
          <div className="py-4 space-y-5">
            {/* Price Stats Trio */}
            <div className="grid grid-cols-3 gap-2.5">
              <div className="p-3 rounded-2xl bg-cream-50 dark:bg-charcoal-800/80 border border-cream-200 dark:border-charcoal-700 text-center">
                <span className="text-[10px] font-bold text-charcoal-500 dark:text-charcoal-400 uppercase tracking-wider flex items-center justify-center gap-0.5">
                  <TrendingDown className="w-3 h-3 text-emerald-500" /> Lowest
                </span>
                <p className="text-sm sm:text-base font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
                  ₹{minPrice ? minPrice.toLocaleString('en-IN') : '—'}
                </p>
              </div>

              <div className="p-3 rounded-2xl bg-cream-50 dark:bg-charcoal-800/80 border border-cream-200 dark:border-charcoal-700 text-center">
                <span className="text-[10px] font-bold text-charcoal-500 dark:text-charcoal-400 uppercase tracking-wider flex items-center justify-center gap-0.5">
                  <IndianRupee className="w-3 h-3 text-forest-500" /> Current
                </span>
                <p className="text-sm sm:text-base font-extrabold text-forest-700 dark:text-sage-300 mt-1">
                  ₹{currPrice ? currPrice.toLocaleString('en-IN') : '—'}
                </p>
              </div>

              <div className="p-3 rounded-2xl bg-cream-50 dark:bg-charcoal-800/80 border border-cream-200 dark:border-charcoal-700 text-center">
                <span className="text-[10px] font-bold text-charcoal-500 dark:text-charcoal-400 uppercase tracking-wider flex items-center justify-center gap-0.5">
                  <TrendingUp className="w-3 h-3 text-amber-500" /> Highest
                </span>
                <p className="text-sm sm:text-base font-extrabold text-amber-600 dark:text-amber-400 mt-1">
                  ₹{maxPrice ? maxPrice.toLocaleString('en-IN') : '—'}
                </p>
              </div>
            </div>

            {/* Chart Area */}
            {snapshots.length > 1 ? (
              <div className="rounded-2xl bg-cream-100/50 dark:bg-charcoal-800 p-4 border border-cream-200 dark:border-charcoal-700">
                <div className="flex items-center justify-between text-[11px] text-charcoal-500 dark:text-charcoal-400 mb-2">
                  <span className="flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-forest-500" /> Verified Trend
                  </span>
                  <span>{snapshots.length} Price Updates</span>
                </div>

                <div className="w-full overflow-x-auto">
                  <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-32 overflow-visible">
                    {/* Grid lines */}
                    <line x1="10" y1="20" x2={chartWidth - 10} y2="20" stroke="currentColor" strokeOpacity="0.1" strokeDasharray="3 3" />
                    <line x1="10" y1={chartHeight / 2} x2={chartWidth - 10} y2={chartHeight / 2} stroke="currentColor" strokeOpacity="0.1" strokeDasharray="3 3" />
                    <line x1="10" y1={chartHeight - 20} x2={chartWidth - 10} y2={chartHeight - 20} stroke="currentColor" strokeOpacity="0.1" strokeDasharray="3 3" />

                    {/* Trend Line */}
                    <path d={pathD} fill="none" stroke="#22c55e" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

                    {/* Data Points */}
                    {points.map((p, i) => (
                      <g key={i}>
                        <circle cx={p.x} cy={p.y} r="4" fill="#22c55e" stroke="#ffffff" strokeWidth="1.5" />
                      </g>
                    ))}
                  </svg>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-2xl bg-cream-50 dark:bg-charcoal-800/60 border border-cream-200 dark:border-charcoal-700 text-center space-y-2">
                <Clock className="w-7 h-7 text-charcoal-400 mx-auto" />
                <p className="text-xs font-semibold text-charcoal-700 dark:text-cream-200">
                  {data?.message || 'Price history will appear after we collect verified price updates.'}
                </p>
                <p className="text-[10px] text-charcoal-500 dark:text-charcoal-400">
                  Initial price snapshot recorded at ₹{currPrice ? currPrice.toLocaleString('en-IN') : '—'}.
                </p>
              </div>
            )}

            {/* Disclaimer */}
            <div className="flex items-center gap-1.5 text-[10px] text-charcoal-500 dark:text-charcoal-400 justify-center">
              <AlertCircle className="w-3 h-3 text-amber-500" />
              <span>Prices verified directly from retailer product feeds</span>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-cream-200 dark:border-charcoal-800 pt-3 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-cream-200 hover:bg-cream-300 dark:bg-charcoal-700 dark:hover:bg-charcoal-600 text-charcoal-800 dark:text-cream-100 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
