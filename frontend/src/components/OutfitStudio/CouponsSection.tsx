import React, { useEffect, useState } from 'react';
import { RetailerCoupon } from '../../types/outfit';
import { outfitStudioService } from '../../services/api';
import {
  Tag,
  Copy,
  Check,
  Calendar,
  ShieldCheck,
  Sparkles,
  Percent,
} from 'lucide-react';

interface CouponsSectionProps {
  retailerFilter?: string;
}

export const CouponsSection: React.FC<CouponsSectionProps> = ({ retailerFilter }) => {
  const [coupons, setCoupons] = useState<RetailerCoupon[]>([]);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    outfitStudioService
      .getCoupons(retailerFilter)
      .then((res) => setCoupons(res || []))
      .catch(() => setCoupons([]))
      .finally(() => setIsLoading(false));
  }, [retailerFilter]);

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <div className="rounded-3xl bg-charcoal-900 border border-charcoal-800 p-5 sm:p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/30">
            <Tag className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-extrabold text-cream-50 flex items-center gap-1.5 uppercase tracking-wide">
              Verified Retailer Coupons <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            </h4>
            <p className="text-[11px] font-medium text-cream-300">
              Verified promotional discounts from approved partner networks
            </p>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 rounded-2xl bg-charcoal-800 animate-pulse" />
          ))}
        </div>
      ) : coupons.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {coupons.map((coupon, i) => (
            <div
              key={coupon.coupon_code || i}
              className="p-4 rounded-2xl bg-charcoal-950 border border-charcoal-800 flex flex-col justify-between space-y-2.5 shadow-md hover:border-amber-500/60 transition"
            >
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                  {coupon.retailer}
                </span>
                {coupon.expiry_date && (
                  <span className="text-[10px] text-cream-400 flex items-center gap-1">
                    <Calendar className="w-2.5 h-2.5" />
                    Exp: {new Date(coupon.expiry_date).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                  </span>
                )}
              </div>

              <div>
                <p className="text-xs font-extrabold text-cream-50">
                  {coupon.discount_text}
                </p>
                {coupon.terms && (
                  <p className="text-[10px] font-medium text-cream-300 line-clamp-2 mt-0.5">
                    {coupon.terms}
                  </p>
                )}
              </div>

              {/* Code Box & Copy */}
              <div className="flex items-center justify-between pt-1 border-t border-charcoal-800">
                <code className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-charcoal-900 border border-charcoal-800 text-emerald-400 tracking-wider">
                  {coupon.coupon_code}
                </code>

                <button
                  onClick={() => handleCopy(coupon.coupon_code)}
                  className={`px-3 py-1 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                    copiedCode === coupon.coupon_code
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'bg-forest-950/80 hover:bg-forest-900 text-sage-300 border border-forest-800'
                  }`}
                >
                  {copiedCode === coupon.coupon_code ? (
                    <>
                      <Check className="w-3.5 h-3.5" /> Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" /> Copy Coupon
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-8 text-center">
          <p className="text-xs font-semibold text-cream-400">
            No verified coupon available.
          </p>
        </div>
      )}
    </div>
  );
};
