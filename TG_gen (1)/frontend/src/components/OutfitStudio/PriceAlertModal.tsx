import React, { useState } from 'react';
import { outfitStudioService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import {
  X,
  BellRing,
  CheckCircle2,
  AlertCircle,
  IndianRupee,
  ShieldCheck,
} from 'lucide-react';

interface PriceAlertModalProps {
  productId: string;
  productTitle: string;
  productUrl: string;
  retailer: string;
  currentPriceInr?: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export const PriceAlertModal: React.FC<PriceAlertModalProps> = ({
  productId,
  productTitle,
  productUrl,
  retailer,
  currentPriceInr,
  isOpen,
  onClose,
}) => {
  const { user } = useAuth();
  const defaultTarget = currentPriceInr ? Math.round(currentPriceInr * 0.85) : 1000;
  const [targetPrice, setTargetPrice] = useState<number>(defaultTarget);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetPrice || targetPrice <= 0) {
      setErrorMessage('Please enter a valid target price in INR.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const res = await outfitStudioService.createPriceAlert({
        product_id: productId,
        product_title: productTitle,
        product_url: productUrl,
        retailer,
        target_price_inr: Number(targetPrice),
        current_price_inr: currentPriceInr || undefined,
      });
      setSuccessMessage(res.message || 'Price alert set successfully!');
      setTimeout(() => {
        setSuccessMessage(null);
        onClose();
      }, 1600);
    } catch (err: any) {
      setErrorMessage(
        err?.response?.data?.detail || 'Failed to configure price alert. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-md rounded-3xl bg-white dark:bg-charcoal-900 border border-cream-200 dark:border-charcoal-700 shadow-2xl p-6 overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 border-b border-cream-200 dark:border-charcoal-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-forest-100 dark:bg-forest-950/60 text-forest-700 dark:text-sage-300 flex items-center justify-center flex-shrink-0">
              <BellRing className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-charcoal-900 dark:text-cream-100">
                Set Price Drop Alert
              </h3>
              <p className="text-[11px] text-charcoal-500 dark:text-charcoal-400">
                {retailer} · Real-time price tracking
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-charcoal-400 hover:text-charcoal-700 dark:hover:text-cream-100 hover:bg-cream-100 dark:hover:bg-charcoal-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        {successMessage ? (
          <div className="py-8 flex flex-col items-center justify-center text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <p className="text-sm font-bold text-charcoal-900 dark:text-cream-100">{successMessage}</p>
            <p className="text-xs text-charcoal-500 dark:text-charcoal-400">
              We will monitor verified price drops for this product.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="py-4 space-y-4">
            <div className="p-3 rounded-2xl bg-cream-50 dark:bg-charcoal-800/80 border border-cream-200 dark:border-charcoal-700 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold text-charcoal-500 dark:text-charcoal-400 uppercase tracking-wider">
                  Product
                </span>
                <p className="text-xs font-bold text-charcoal-800 dark:text-cream-200 line-clamp-1">
                  {productTitle}
                </p>
              </div>
              {currentPriceInr && (
                <div className="text-right flex-shrink-0 ml-2">
                  <span className="text-[10px] text-charcoal-500 dark:text-charcoal-400">Current</span>
                  <p className="text-xs font-extrabold text-forest-700 dark:text-sage-300">
                    ₹{currentPriceInr.toLocaleString('en-IN')}
                  </p>
                </div>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold text-charcoal-700 dark:text-cream-200 mb-1.5">
                Target Alert Price (INR)
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-charcoal-400">
                  <IndianRupee className="w-4 h-4" />
                </div>
                <input
                  type="number"
                  min="50"
                  max="200000"
                  step="50"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(Number(e.target.value))}
                  placeholder="Enter target price"
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-white dark:bg-charcoal-800 text-charcoal-900 dark:text-cream-100 text-sm font-semibold focus:ring-2 focus:ring-forest-500 focus:border-transparent transition"
                  required
                />
              </div>
              <p className="text-[10px] text-charcoal-500 dark:text-charcoal-400 mt-1">
                You will be alerted when a fresh verified price drops to or below ₹{targetPrice?.toLocaleString('en-IN') || 0}.
              </p>
            </div>

            {/* Quick discount chip buttons */}
            {currentPriceInr && (
              <div className="flex items-center gap-1.5 pt-1">
                <span className="text-[10px] font-bold text-charcoal-500 dark:text-charcoal-400 mr-1">Quick:</span>
                {[10, 20, 30].map((pct) => {
                  const val = Math.round(currentPriceInr * (1 - pct / 100));
                  return (
                    <button
                      key={pct}
                      type="button"
                      onClick={() => setTargetPrice(val)}
                      className="px-2.5 py-1 rounded-lg text-[10px] font-semibold bg-cream-100 dark:bg-charcoal-800 text-charcoal-700 dark:text-cream-200 border border-cream-200 dark:border-charcoal-700 hover:border-forest-500 transition"
                    >
                      -{pct}% (₹{val.toLocaleString('en-IN')})
                    </button>
                  );
                })}
              </div>
            )}

            {errorMessage && (
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs text-rose-600 dark:text-rose-400 flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div className="flex items-center justify-between pt-2">
              <span className="text-[10px] text-charcoal-400 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-forest-500" /> Only verified live prices trigger alerts
              </span>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-forest-700 hover:bg-forest-600 text-cream-100 shadow-sm transition flex items-center gap-1.5 disabled:opacity-50"
              >
                <BellRing className="w-3.5 h-3.5" />
                {isSubmitting ? 'Setting Alert…' : 'Set Alert'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
