import React from 'react';
import { OutfitItem, getItemCategoryIcon } from '../../types/outfit';
import { Leaf, IndianRupee } from 'lucide-react';

interface OutfitItemCardProps {
  item: OutfitItem;
  index: number;
}

export const OutfitItemCard: React.FC<OutfitItemCardProps> = ({ item, index }) => {
  const icon = getItemCategoryIcon(item.category, item.name);
  const colorIsHex = item.color?.startsWith('#');

  return (
    <div
      className="flex items-start gap-3 p-4 rounded-2xl border border-charcoal-800 bg-charcoal-900 text-cream-100 hover:border-forest-600/60 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200"
      style={{
        animationDelay: `${index * 60}ms`,
        animation: 'fadeSlideUp 0.35s ease forwards',
        opacity: 0,
      }}
    >
      {/* Category icon badge */}
      <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-charcoal-800 text-sage-300 flex items-center justify-center text-lg border border-charcoal-700">
        {icon}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <span className="text-[10px] font-bold text-forest-400 uppercase tracking-widest">
              {item.category}
            </span>
            <p className="text-sm font-bold text-cream-50 leading-snug truncate">
              {item.name}
            </p>
          </div>

          <div className="flex-shrink-0 flex flex-col items-end gap-1">
            {/* Color swatch */}
            {item.color && (
              <div
                className="w-5 h-5 rounded-full border-2 border-charcoal-700 shadow-sm"
                title={item.color}
                style={{ backgroundColor: colorIsHex ? item.color : '#7D9B76' }}
              />
            )}
            {/* Price */}
            {item.estimated_price_inr != null && (
              <span className="text-xs font-extrabold text-emerald-400 flex items-center gap-0.5">
                <IndianRupee className="w-3 h-3" />
                {item.estimated_price_inr.toLocaleString('en-IN')}
              </span>
            )}
          </div>
        </div>

        {/* Fabric chip */}
        {item.recommended_fabric && (
          <span className="inline-block mt-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-forest-950/90 text-sage-200 border border-forest-800/80">
            🧵 {item.recommended_fabric}
          </span>
        )}

        {/* Sustainability note */}
        {item.sustainability_note && (
          <div className="flex items-start gap-1.5 mt-2">
            <Leaf className="w-3.5 h-3.5 text-forest-400 flex-shrink-0 mt-0.5" />
            <p className="text-[11px] font-medium text-charcoal-300 leading-relaxed">
              {item.sustainability_note}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
