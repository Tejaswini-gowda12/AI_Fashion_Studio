import React, { useState } from 'react';
import { GeneratedImageInfo, GeneratedOutfitImageVariation } from '../../types/outfit';
import {
  Sparkles,
  RefreshCw,
  Download,
  Share2,
  Maximize2,
  X,
  Info,
  Layers,
  Check,
  Eye,
  AlertCircle,
} from 'lucide-react';

interface ConceptVariationsGalleryProps {
  primaryImage: GeneratedImageInfo;
  variations: GeneratedOutfitImageVariation[];
  outfitName: string;
  onRegenerateVariation: (variationIndex: number) => Promise<void>;
  isRegenerating: boolean;
}

export const ConceptVariationsGallery: React.FC<ConceptVariationsGalleryProps> = ({
  primaryImage,
  variations,
  outfitName,
  onRegenerateVariation,
  isRegenerating,
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [modalOpen, setModalOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const activeVariation = variations[selectedIndex] || {
    variation_index: 1,
    variation_title: 'Editorial Fashion Concept',
    image_url: primaryImage.url || '',
    status: primaryImage.status,
    label: primaryImage.disclaimer,
    prompt: primaryImage.prompt,
  };

  const isDemo = activeVariation.status === 'demo' || primaryImage.status === 'demo';

  const handleDownload = () => {
    if (!activeVariation.image_url) return;
    const link = document.createElement('a');
    link.href = activeVariation.image_url;
    link.target = '_blank';
    link.download = `ecofabric-outfit-concept-var${activeVariation.variation_index}.jpg`;
    link.click();
  };

  const handleShare = async () => {
    const text = `Check out this AI outfit concept: ${outfitName} 🌿 (AI-generated style concept — not an exact purchasable product.)`;
    if (navigator.share) {
      try {
        await navigator.share({ title: outfitName, text, url: window.location.href });
      } catch {
        // dismissed
      }
    } else {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <section className="rounded-3xl bg-white dark:bg-charcoal-900 border border-cream-200 dark:border-charcoal-800 shadow-sm overflow-hidden animate-fadeSlideUp">
      {/* Header */}
      <div className="p-4 sm:p-5 border-b border-cream-200 dark:border-charcoal-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-cream-50/50 dark:bg-charcoal-850">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm sm:text-base font-bold text-forest-950 dark:text-cream-100 flex items-center gap-2 uppercase tracking-wide">
              <Eye className="w-4 h-4 text-forest-600 dark:text-forest-400" /> AI Outfit Concept Visualizations
            </h3>
            <span className="text-[11px] px-2 py-0.5 rounded-full font-bold bg-forest-100 dark:bg-forest-950 text-forest-800 dark:text-forest-300 border border-forest-300 dark:border-forest-700">
              {variations.length} Variations
            </span>
          </div>
          <p className="text-xs font-medium text-forest-900 dark:text-cream-300 mt-0.5">
            Photorealistic style concepts generated for this garment silhouette and fabric choice.
          </p>
        </div>

        {isDemo && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-950/60 border border-amber-300 dark:border-amber-700 text-[11px] text-amber-800 dark:text-amber-200 font-medium">
            <Info className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
            <span>Demo Concept View</span>
          </div>
        )}
      </div>

      {/* Demo unconfigured warning banner if applicable */}
      {isDemo && primaryImage.message && (
        <div className="p-3.5 bg-amber-50/80 dark:bg-amber-950/40 border-b border-amber-200 dark:border-amber-800/60 flex items-start gap-2.5 text-xs text-amber-900 dark:text-amber-200">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Notice:</strong> {primaryImage.message}
          </div>
        </div>
      )}

      {/* Main Image Stage */}
      <div className="relative bg-charcoal-950 flex items-center justify-center p-3 sm:p-5 overflow-hidden group min-h-[380px] sm:min-h-[460px]">
        {activeVariation.image_url ? (
          <img
            src={activeVariation.image_url}
            alt={`${outfitName} - ${activeVariation.variation_title}`}
            className="w-full max-h-[560px] object-contain rounded-2xl shadow-2xl transition-transform duration-300"
          />
        ) : (
          <div className="text-center p-8 text-charcoal-400">
            <Sparkles className="w-8 h-8 mx-auto mb-2 text-forest-400 animate-pulse" />
            <p className="text-sm">Rendering concept visualization…</p>
          </div>
        )}

        {/* Mandatory AI-generated style concept label on top of image */}
        <div className="absolute top-5 left-5 z-10 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-charcoal-900/85 text-cream-100 backdrop-blur-md border border-white/20 shadow-lg flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>{activeVariation.label || 'AI-generated style concept — not an exact purchasable product.'}</span>
        </div>

        {/* Variation Title Badge */}
        <div className="absolute bottom-5 left-5 z-10 px-3 py-1 rounded-xl text-xs font-bold bg-charcoal-900/85 text-sage-200 backdrop-blur-md border border-charcoal-700 shadow-md flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-sage-400" />
          <span>Variation {activeVariation.variation_index}: {activeVariation.variation_title}</span>
        </div>

        {/* Fullscreen Button */}
        <button
          onClick={() => setModalOpen(true)}
          className="absolute top-5 right-5 z-10 p-2 rounded-xl bg-charcoal-900/80 hover:bg-charcoal-800 text-cream-100 backdrop-blur-md border border-white/20 shadow-md transition"
          title="View Fullscreen"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Variation Thumbnails Selector Bar */}
      {variations.length > 1 && (
        <div className="p-3 sm:p-4 bg-cream-100/60 dark:bg-charcoal-850 border-t border-cream-200 dark:border-charcoal-800 flex items-center gap-3 overflow-x-auto">
          <span className="text-xs font-bold text-charcoal-600 dark:text-charcoal-300 uppercase tracking-wide flex-shrink-0">
            Variations:
          </span>
          <div className="flex items-center gap-3 flex-nowrap">
            {variations.map((v, i) => {
              const isSelected = i === selectedIndex;
              return (
                <button
                  key={v.variation_index || i}
                  type="button"
                  onClick={() => setSelectedIndex(i)}
                  className={`group relative flex items-center gap-2.5 p-1.5 pr-3 rounded-xl border transition-all ${
                    isSelected
                      ? 'bg-white dark:bg-charcoal-800 border-forest-600 dark:border-forest-400 shadow-md ring-2 ring-forest-500/20'
                      : 'bg-white/60 dark:bg-charcoal-800/60 border-cream-200 dark:border-charcoal-700 hover:border-forest-400'
                  }`}
                >
                  <img
                    src={v.image_url}
                    alt={v.variation_title}
                    className="w-10 h-10 object-cover rounded-lg flex-shrink-0"
                  />
                  <div className="text-left">
                    <p className={`text-xs font-bold leading-tight ${isSelected ? 'text-forest-800 dark:text-forest-300' : 'text-charcoal-700 dark:text-cream-200'}`}>
                      Var {v.variation_index}
                    </p>
                    <p className="text-[10px] text-charcoal-500 dark:text-charcoal-400 truncate max-w-[110px]">
                      {v.variation_title}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 p-4 bg-white dark:bg-charcoal-900 border-t border-cream-200 dark:border-charcoal-800">
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => onRegenerateVariation(activeVariation.variation_index)}
            disabled={isRegenerating}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-charcoal-800 dark:text-cream-100 bg-cream-100 dark:bg-charcoal-800 hover:bg-cream-200 dark:hover:bg-charcoal-700 transition disabled:opacity-50 border border-cream-200 dark:border-charcoal-700 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? 'animate-spin text-forest-600' : ''}`} />
            <span>Regenerate Variation {activeVariation.variation_index}</span>
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-charcoal-800 dark:text-cream-200 bg-white dark:bg-charcoal-800 hover:bg-cream-100 dark:hover:bg-charcoal-700 transition border border-cream-200 dark:border-charcoal-700 shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Concept</span>
          </button>

          <button
            onClick={handleShare}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-charcoal-800 dark:text-cream-200 bg-white dark:bg-charcoal-800 hover:bg-cream-100 dark:hover:bg-charcoal-700 transition border border-cream-200 dark:border-charcoal-700 shadow-sm"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-forest-600" /> : <Share2 className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Share'}</span>
          </button>
        </div>

        <p className="text-[11px] text-charcoal-500 dark:text-charcoal-400 italic">
          * AI-generated style concept — not an exact purchasable product.
        </p>
      </div>

      {/* Fullscreen Zoom Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4">
          <div className="relative max-w-5xl w-full flex flex-col items-center">
            <button
              onClick={() => setModalOpen(false)}
              className="absolute -top-12 right-0 p-2 text-white/80 hover:text-white rounded-full bg-white/10 transition"
            >
              <X className="w-6 h-6" />
            </button>
            <img
              src={activeVariation.image_url}
              alt={outfitName}
              className="max-h-[85vh] w-auto object-contain rounded-2xl shadow-2xl border border-white/20"
            />
            <div className="mt-3 px-4 py-1.5 rounded-full bg-charcoal-900/80 text-cream-100 text-xs border border-white/20 shadow">
              {activeVariation.label || 'AI-generated style concept — not an exact purchasable product.'}
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
