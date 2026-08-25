import React from 'react';
import { Outfit } from '../../types/outfit';
import { Leaf, Star, DollarSign, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';

interface OutfitConceptCardProps {
  outfit: Outfit;
  isMockMode?: boolean;
  generatedImageUrl?: string | null;
}

const ScoreRing: React.FC<{ score: number }> = ({ score }) => {
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? '#4ade80' : score >= 60 ? '#fbbf24' : '#f87171';

  return (
    <div className="relative w-20 h-20 flex items-center justify-center flex-shrink-0">
      <svg width="80" height="80" className="rotate-[-90deg]">
        <circle cx="40" cy="40" r={radius} fill="none" stroke="#374151" strokeWidth="6" />
        <circle
          cx="40" cy="40" r={radius} fill="none"
          stroke={color} strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-lg font-bold" style={{ color }}>
          {score}
        </span>
        <span className="text-[9px] text-charcoal-500 dark:text-charcoal-400 uppercase tracking-wider font-semibold">Eco</span>
      </div>
    </div>
  );
};

export const OutfitConceptCard: React.FC<OutfitConceptCardProps> = ({
  outfit,
  isMockMode,
  generatedImageUrl,
}) => {
  return (
    <section className="generated-concept-card border border-charcoal-800 bg-charcoal-900 text-cream-100 shadow-xl rounded-3xl overflow-hidden">
      {/* Absolute badge placed at top: 20px, left: 20px */}
      <span className="generated-concept-badge px-3.5 py-1.5 rounded-full text-xs font-bold bg-charcoal-950/90 text-cream-50 backdrop-blur-md border border-forest-500/40 shadow-sm flex items-center gap-1.5">
        ✨ AI-generated style concept
      </span>

      {/* Content wrapper with padding-top: 76px so badge never overlaps text or buttons */}
      <div className="generated-concept-content px-5 sm:px-6 pb-6 space-y-6">
        {/* Header section */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-2">
              {outfit.occasion && (
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-forest-900 text-sage-200 border border-forest-700">
                  {outfit.occasion}
                </span>
              )}
              {isMockMode && (
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-950/60 text-amber-300 border border-amber-700/50">
                  Demo Concept
                </span>
              )}
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-cream-50 leading-tight tracking-tight">
              {outfit.outfit_name}
            </h2>
            <p className="mt-2 text-sm sm:text-base text-cream-200 leading-relaxed font-medium">
              {outfit.description}
            </p>
          </div>

          {outfit.sustainability_score != null && (
            <div className="flex-shrink-0 self-start sm:self-auto">
              <ScoreRing score={outfit.sustainability_score} />
            </div>
          )}
        </div>

        {/* Colour palette strip */}
        {outfit.color_palette.length > 0 && (
          <div className="p-3.5 rounded-xl bg-charcoal-950/80 border border-charcoal-800 flex flex-wrap items-center gap-3">
            <span className="text-xs font-bold text-cream-200 uppercase tracking-wide">
              Suggested Color Palette:
            </span>
            <div className="flex items-center gap-2">
              {outfit.color_palette.map((hex, i) => (
                <div key={i} className="flex items-center gap-1.5">
                  <div
                    title={hex}
                    className="w-7 h-7 rounded-full border-2 border-charcoal-700 shadow-sm"
                    style={{ backgroundColor: hex.startsWith('#') ? hex : '#7D9B76' }}
                  />
                  <span className="text-[11px] font-mono font-semibold text-cream-300">
                    {hex}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stats summary row */}
        <div className="grid grid-cols-3 divide-x divide-charcoal-800 border-y border-charcoal-800 py-3 bg-charcoal-950/60 rounded-xl">
          <div className="px-3 sm:px-4 text-center">
            <Leaf className="w-4 h-4 text-forest-400 mx-auto mb-1" />
            <p className="text-[11px] font-semibold text-charcoal-400">Key Fabrics</p>
            <p className="text-xs sm:text-sm font-bold text-cream-100 truncate">
              {outfit.recommended_fabrics.slice(0, 2).join(', ') || 'Eco Fabrics'}
            </p>
          </div>
          <div className="px-3 sm:px-4 text-center">
            <DollarSign className="w-4 h-4 text-sage-400 mx-auto mb-1" />
            <p className="text-[11px] font-semibold text-charcoal-400">Est. Total</p>
            <p className="text-xs sm:text-sm font-bold text-cream-100">
              {outfit.total_estimated_price_inr
                ? `₹${outfit.total_estimated_price_inr.toLocaleString('en-IN')}`
                : 'Custom'}
            </p>
          </div>
          <div className="px-3 sm:px-4 text-center">
            <Star className="w-4 h-4 text-amber-400 mx-auto mb-1" />
            <p className="text-[11px] font-semibold text-charcoal-400">Curated Items</p>
            <p className="text-xs sm:text-sm font-bold text-cream-100">
              {outfit.items.length} garments
            </p>
          </div>
        </div>

        {/* Sustainability explanation */}
        {outfit.sustainability_summary && (
          <div className="p-4 rounded-2xl bg-forest-950/70 border border-forest-800/80 flex items-start gap-3">
            <Leaf className="w-5 h-5 text-forest-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-forest-300 uppercase tracking-wide mb-1">
                Sustainability Impact
              </p>
              <p className="text-xs sm:text-sm font-medium text-sage-100 leading-relaxed">
                {outfit.sustainability_summary}
              </p>
            </div>
          </div>
        )}

        {/* Styling tips */}
        {outfit.styling_tips && outfit.styling_tips.length > 0 && (
          <div>
            <p className="text-xs font-bold text-cream-200 uppercase tracking-wide mb-2.5 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-400" /> Styling & Fit Tips
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {outfit.styling_tips.map((tip, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2.5 p-3.5 rounded-xl bg-charcoal-950/80 border border-charcoal-800 text-xs sm:text-sm font-medium text-cream-100"
                >
                  <CheckCircle2 className="w-4 h-4 text-forest-400 flex-shrink-0 mt-0.5" />
                  <span className="leading-snug">{tip}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
