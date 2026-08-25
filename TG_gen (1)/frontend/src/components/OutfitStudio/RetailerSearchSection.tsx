import React from 'react';
import { RetailerSearchLink } from '../../types/outfit';
import { ExternalLink, ShoppingBag, ShieldCheck, Search, Sparkles } from 'lucide-react';

interface RetailerSearchSectionProps {
  searchLinks: RetailerSearchLink[];
  outfitName: string;
  storeVerificationNotice: string;
}

const STORE_CONFIG: Record<
  string,
  {
    bgGradient: string;
    badgeBg: string;
    textColor: string;
    borderColor: string;
    description: string;
    accentEmoji: string;
  }
> = {
  Myntra: {
    bgGradient: 'from-rose-950/40 via-charcoal-900 to-charcoal-900',
    badgeBg: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
    textColor: 'text-rose-400',
    borderColor: 'border-rose-900/60 hover:border-rose-500',
    description: 'Explore trending dresses, western wear & curated brands on Myntra',
    accentEmoji: '🛍️',
  },
  AJIO: {
    bgGradient: 'from-amber-950/40 via-charcoal-900 to-charcoal-900',
    badgeBg: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    textColor: 'text-amber-400',
    borderColor: 'border-amber-900/60 hover:border-amber-500',
    description: 'Find handpicked indie styles, linen ensembles & western co-ords on AJIO',
    accentEmoji: '✨',
  },
  'Nykaa Fashion': {
    bgGradient: 'from-pink-950/40 via-charcoal-900 to-charcoal-900',
    badgeBg: 'bg-pink-500/20 text-pink-300 border-pink-500/40',
    textColor: 'text-pink-400',
    borderColor: 'border-pink-900/60 hover:border-pink-500',
    description: 'Premium curated designer labels, sustainable collections & footwear',
    accentEmoji: '🌸',
  },
  'Amazon India': {
    bgGradient: 'from-orange-950/40 via-charcoal-900 to-charcoal-900',
    badgeBg: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
    textColor: 'text-orange-400',
    borderColor: 'border-orange-900/60 hover:border-orange-500',
    description: 'Fast delivery across India with broad catalog options and reviews',
    accentEmoji: '📦',
  },
  'Tata CLiQ': {
    bgGradient: 'from-indigo-950/40 via-charcoal-900 to-charcoal-900',
    badgeBg: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
    textColor: 'text-indigo-400',
    borderColor: 'border-indigo-900/60 hover:border-indigo-500',
    description: 'Authentic brand storefronts, luxury and sustainable fashion selections',
    accentEmoji: '💎',
  },
};

export const RetailerSearchSection: React.FC<RetailerSearchSectionProps> = ({
  searchLinks,
  outfitName,
  storeVerificationNotice,
}) => {
  return (
    <section className="rounded-3xl bg-charcoal-900 border border-charcoal-800 shadow-xl p-5 sm:p-6 animate-fadeSlideUp">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
        <div>
          <h3 className="text-sm sm:text-base font-extrabold text-cream-50 flex items-center gap-2 uppercase tracking-wide">
            <Search className="w-4 h-4 text-forest-400" /> Search on Indian Stores
          </h3>
          <p className="text-xs text-cream-300 font-medium mt-0.5">
            Launch verified keyword searches for this outfit across India's top fashion retailers.
          </p>
        </div>

        <span className="self-start sm:self-auto text-[11px] font-bold px-3 py-1 rounded-full bg-forest-950 text-forest-300 border border-forest-800 flex items-center gap-1 shadow-sm">
          <ShieldCheck className="w-3.5 h-3.5 text-forest-400" /> Direct Retailer Links
        </span>
      </div>

      {/* Store cards grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5 mt-4">
        {searchLinks.map((link) => {
          const cfg = STORE_CONFIG[link.retailer] || {
            bgGradient: 'from-forest-950/40 via-charcoal-900 to-charcoal-900',
            badgeBg: 'bg-forest-500/20 text-forest-300 border-forest-500/40',
            textColor: 'text-forest-400',
            borderColor: 'border-charcoal-700 hover:border-forest-500',
            description: `Search for ${outfitName} on ${link.retailer}`,
            accentEmoji: link.icon || '🛍️',
          };

          return (
            <a
              key={link.retailer}
              id={`search-store-${link.retailer.replace(/\s+/g, '-').toLowerCase()}`}
              href={link.search_url}
              target="_blank"
              rel="noopener noreferrer"
              className={`group flex flex-col justify-between p-4 rounded-2xl border bg-gradient-to-br ${cfg.bgGradient} bg-charcoal-900 ${cfg.borderColor} shadow-lg hover:shadow-2xl hover:-translate-y-1 transition-all duration-300`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{cfg.accentEmoji}</span>
                    <h4 className="text-sm font-extrabold text-cream-50">
                      {link.retailer}
                    </h4>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border shadow-sm ${cfg.badgeBg}`}>
                    Direct Search
                  </span>
                </div>

                <p className="text-xs text-cream-200 font-medium leading-snug line-clamp-2">
                  {cfg.description}
                </p>

                <div className="mt-2.5 p-2 rounded-lg bg-charcoal-950 border border-charcoal-800 text-[11px] text-cream-300 font-mono truncate shadow-inner">
                  🔍 "{link.query}"
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-charcoal-800 flex items-center justify-between">
                <span className="text-xs font-bold text-sage-300 group-hover:text-cream-50 group-hover:underline transition-colors">
                  Search on {link.retailer}
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-charcoal-400 group-hover:text-cream-50 transition-colors" />
              </div>
            </a>
          );
        })}
      </div>

      {/* Mandatory verified notice */}
      <div className="mt-5 p-3.5 rounded-2xl bg-charcoal-950 border border-charcoal-800 flex items-start gap-2.5 shadow-sm">
        <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-cream-200 font-medium leading-relaxed">
          <strong className="text-cream-50">Store Verification Notice:</strong> {storeVerificationNotice || 'Prices, stock, sizes, and fabric details are verified on the retailer website.'}
        </p>
      </div>
    </section>
  );
};
