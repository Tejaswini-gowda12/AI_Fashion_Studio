import React, { useState, useMemo } from 'react';
import {
  ExternalLink,
  Bookmark,
  BookmarkCheck,
  ShieldCheck,
  Building2,
  ShoppingBag,
  FileText,
  HelpCircle,
  AlertTriangle,
  Sparkles,
  Search,
  Filter,
  CheckCircle2,
  Info,
  Layers,
  Tag,
  ArrowUpRight,
  RefreshCw,
  SlidersHorizontal,
  ChevronRight,
  BadgeCheck
} from 'lucide-react';
import {
  VisualSearchResponse,
  VisualSearchMatch,
  VisualSearchFilter,
  SourceReliability,
  SaveMatchRequest
} from '../types';

interface VisualSearchResultsProps {
  results: VisualSearchResponse | null;
  isLoading: boolean;
  error: string | null;
  onRetry?: () => void;
  onSaveMatch?: (match: VisualSearchMatch) => Promise<boolean>;
  savedMatchUrls?: Set<string>;
}

export const VisualSearchResults: React.FC<VisualSearchResultsProps> = ({
  results,
  isLoading,
  error,
  onRetry,
  onSaveMatch,
  savedMatchUrls = new Set()
}) => {
  const [activeFilter, setActiveFilter] = useState<VisualSearchFilter>('all');
  const [localSavedUrls, setLocalSavedUrls] = useState<Set<string>>(savedMatchUrls);
  const [savingUrl, setSavingUrl] = useState<string | null>(null);
  const [saveToast, setSaveToast] = useState<string | null>(null);

  const handleSave = async (match: VisualSearchMatch) => {
    if (localSavedUrls.has(match.source_url) || savingUrl === match.source_url) return;
    setSavingUrl(match.source_url);
    try {
      if (onSaveMatch) {
        const success = await onSaveMatch(match);
        if (success) {
          setLocalSavedUrls((prev) => new Set([...prev, match.source_url]));
          setSaveToast(`Saved "${match.title || match.source_domain}" to your project inspiration!`);
          setTimeout(() => setSaveToast(null), 3500);
        }
      } else {
        setLocalSavedUrls((prev) => new Set([...prev, match.source_url]));
        setSaveToast(`Saved to inspiration collection!`);
        setTimeout(() => setSaveToast(null), 3500);
      }
    } catch (err) {
      console.error('Failed to save match:', err);
    } finally {
      setSavingUrl(null);
    }
  };

  const filteredMatches = useMemo(() => {
    if (!results || !results.matches) return [];
    let matches = [...results.matches];

    switch (activeFilter) {
      case 'official':
        return matches.filter((m) => m.source_reliability === 'official_brand');
      case 'products':
        return matches.filter((m) => m.source_reliability === 'official_brand' || m.source_reliability === 'retailer');
      case 'fabric_refs':
        return matches.filter((m) => m.fabric_text_found && m.verification_status === 'source_text_found');
      case 'top_match':
        return matches.sort((a, b) => b.match_score - a.match_score).slice(0, 5);
      case 'all':
      default:
        return matches;
    }
  }, [results, activeFilter]);

  const getReliabilityBadge = (reliability: SourceReliability) => {
    switch (reliability) {
      case 'official_brand':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
            <BadgeCheck className="w-3.5 h-3.5" />
            Official Brand / Manufacturer
          </span>
        );
      case 'retailer':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border border-blue-300 dark:border-blue-700">
            <ShoppingBag className="w-3.5 h-3.5" />
            Retailer Listing
          </span>
        );
      case 'blog_editorial':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 border border-purple-300 dark:border-purple-700">
            <FileText className="w-3.5 h-3.5" />
            Blog / Editorial
          </span>
        );
      case 'unknown':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300 border border-stone-300 dark:border-stone-700">
            <HelpCircle className="w-3.5 h-3.5" />
            Web Reference
          </span>
        );
    }
  };

  const getMatchScoreBadge = (score: number) => {
    const percentage = Math.round(score * 100);
    let colorClass = 'bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300 border-stone-300';
    if (percentage >= 85) {
      colorClass = 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700';
    } else if (percentage >= 70) {
      colorClass = 'bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300 border-amber-300 dark:border-amber-700';
    }

    return (
      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-bold border ${colorClass}`}>
        <Sparkles className="w-3 h-3 text-amber-500" />
        <span>{percentage}% Visual Match</span>
      </div>
    );
  };

  // Loading skeleton state
  if (isLoading) {
    return (
      <div className="mt-8 rounded-2xl bg-white/90 dark:bg-stone-900/90 backdrop-blur-md border border-stone-200/80 dark:border-stone-800 p-6 md:p-8 shadow-xl">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="relative mb-5">
            <div className="w-16 h-16 rounded-full border-4 border-emerald-500/20 border-t-emerald-600 dark:border-t-emerald-400 animate-spin flex items-center justify-center">
              <Search className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <Sparkles className="w-5 h-5 text-amber-500 absolute -top-1 -right-1 animate-pulse" />
          </div>
          <h3 className="text-xl font-bold text-stone-900 dark:text-stone-100">
            Searching for visually similar products…
          </h3>
          <p className="text-sm text-stone-600 dark:text-stone-400 mt-2 max-w-md">
            Querying legal visual search providers, parsing garment details, and extracting verified source descriptions.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mt-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse bg-stone-100 dark:bg-stone-800/60 rounded-xl p-4 border border-stone-200 dark:border-stone-700 h-64 flex flex-col justify-between">
                <div className="h-32 bg-stone-200 dark:bg-stone-700 rounded-lg w-full mb-3" />
                <div className="h-4 bg-stone-200 dark:bg-stone-700 rounded w-3/4 mb-2" />
                <div className="h-3 bg-stone-200 dark:bg-stone-700 rounded w-1/2" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="mt-8 rounded-2xl bg-white/90 dark:bg-stone-900/90 backdrop-blur-md border border-rose-200 dark:border-rose-900/50 p-6 md:p-8 shadow-xl">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 rounded-xl">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-stone-900 dark:text-stone-100">
              Visual Search Unavailable
            </h3>
            <p className="text-sm text-stone-600 dark:text-stone-400 mt-1">
              {error}
            </p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white transition-colors shadow-sm"
              >
                <RefreshCw className="w-4 h-4" />
                Retry Search
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!results) return null;

  return (
    <div className="mt-8 rounded-2xl bg-white/95 dark:bg-stone-900/95 backdrop-blur-md border border-stone-200/90 dark:border-stone-800 p-6 md:p-8 shadow-xl transition-all">
      {/* Toast Notification */}
      {saveToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-stone-900 text-white dark:bg-stone-100 dark:text-stone-900 rounded-xl shadow-2xl border border-stone-700 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 dark:text-emerald-600" />
          <span className="text-sm font-medium">{saveToast}</span>
        </div>
      )}

      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-stone-200 dark:border-stone-800">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400">
              <Search className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl md:text-2xl font-black tracking-tight text-stone-900 dark:text-stone-100">
                Web Visual Matches
              </h2>
              <p className="text-xs uppercase tracking-wider font-bold text-amber-600 dark:text-amber-400 mt-0.5">
                Visual Lookalikes — Not Fabric Confirmation
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-medium text-stone-500 dark:text-stone-400 bg-stone-100 dark:bg-stone-800/80 px-3 py-1.5 rounded-lg">
          <span>Provider:</span>
          <span className="font-semibold text-stone-800 dark:text-stone-200 uppercase">
            {results.provider_used}
          </span>
          <span className="text-stone-300 dark:text-stone-700">•</span>
          <span>{results.matches.length} matches</span>
        </div>
      </div>

      {/* Strict 3-Tier Clarity Banner */}
      <div className="mt-6 p-4 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200/80 dark:border-amber-800/60 text-stone-800 dark:text-stone-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          <div className="text-xs md:text-sm space-y-2">
            <p className="font-semibold text-amber-900 dark:text-amber-200">
              {results.disclaimer}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 font-mono text-xs">
              <div className="p-2 rounded-lg bg-white/70 dark:bg-stone-900/60 border border-amber-200/60 dark:border-amber-900/40">
                <span className="font-bold text-stone-900 dark:text-stone-100 block">1. AI Fabric Estimate</span>
                <span className="text-stone-600 dark:text-stone-400 text-[11px]">Computer vision surface texture inference</span>
              </div>
              <div className="p-2 rounded-lg bg-white/70 dark:bg-stone-900/60 border border-amber-200/60 dark:border-amber-900/40">
                <span className="font-bold text-stone-900 dark:text-stone-100 block">2. Web Visual Matches</span>
                <span className="text-stone-600 dark:text-stone-400 text-[11px]">Visually similar garments found across web</span>
              </div>
              <div className="p-2 rounded-lg bg-white/70 dark:bg-stone-900/60 border border-amber-200/60 dark:border-amber-900/40">
                <span className="font-bold text-stone-900 dark:text-stone-100 block">3. Verified Source Text</span>
                <span className="text-stone-600 dark:text-stone-400 text-[11px]">Only confirmed if stated directly on product page</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Related Entities / Tags */}
      {results.related_entities && results.related_entities.length > 0 && (
        <div className="mt-5 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-stone-500 dark:text-stone-400 flex items-center gap-1">
            <Tag className="w-3.5 h-3.5" />
            Related Entities:
          </span>
          {results.related_entities.map((entity, idx) => (
            <span
              key={idx}
              className="px-2.5 py-1 text-xs font-medium rounded-md bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 border border-stone-200 dark:border-stone-700/80"
            >
              {entity}
            </span>
          ))}
        </div>
      )}

      {/* Filter Tabs */}
      <div className="mt-6 flex flex-wrap items-center gap-2 border-b border-stone-200 dark:border-stone-800 pb-3">
        <div className="flex items-center gap-1.5 text-xs font-bold text-stone-500 dark:text-stone-400 mr-2">
          <SlidersHorizontal className="w-3.5 h-3.5" />
          Filter:
        </div>
        {[
          { id: 'all' as VisualSearchFilter, label: `All Results (${results.matches.length})` },
          { id: 'official' as VisualSearchFilter, label: 'Official Sources' },
          { id: 'products' as VisualSearchFilter, label: 'Products & Retailers' },
          { id: 'fabric_refs' as VisualSearchFilter, label: 'Explicit Fabric Text' },
          { id: 'top_match' as VisualSearchFilter, label: 'Highest Visual Match' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveFilter(tab.id)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeFilter === tab.id
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Matches Grid */}
      {filteredMatches.length === 0 ? (
        <div className="py-12 text-center">
          <Info className="w-8 h-8 text-stone-400 mx-auto mb-2" />
          <p className="text-sm font-semibold text-stone-700 dark:text-stone-300">
            No matches found for the selected filter.
          </p>
          <button
            onClick={() => setActiveFilter('all')}
            className="mt-3 text-xs font-bold text-emerald-600 dark:text-emerald-400 hover:underline"
          >
            Reset filter to see all results
          </button>
        </div>
      ) : (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredMatches.map((match, index) => {
            const isSaved = localSavedUrls.has(match.source_url);
            const isSaving = savingUrl === match.source_url;

            return (
              <div
                key={index}
                className="group flex flex-col justify-between rounded-xl bg-stone-50/70 dark:bg-stone-800/50 border border-stone-200 dark:border-stone-700/80 hover:border-emerald-500/50 dark:hover:border-emerald-500/50 hover:shadow-lg transition-all duration-200 overflow-hidden"
              >
                <div>
                  {/* Thumbnail & Badges Header */}
                  <div className="relative h-48 w-full bg-stone-200 dark:bg-stone-800 overflow-hidden">
                    {match.thumbnail_url ? (
                      <img
                        src={match.thumbnail_url}
                        alt={match.title || 'Product Match'}
                        className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          // Fallback to placeholder on error
                          (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=400&q=80';
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-stone-400">
                        <ShoppingBag className="w-12 h-12 stroke-[1.5]" />
                      </div>
                    )}

                    <div className="absolute top-2.5 left-2.5 flex flex-col gap-1 items-start">
                      {getMatchScoreBadge(match.match_score)}
                    </div>

                    <div className="absolute top-2.5 right-2.5">
                      <button
                        onClick={() => handleSave(match)}
                        disabled={isSaved || isSaving}
                        title={isSaved ? 'Saved to project' : 'Save match as inspiration'}
                        className={`p-2 rounded-lg backdrop-blur-md transition-all ${
                          isSaved
                            ? 'bg-emerald-600 text-white shadow'
                            : 'bg-white/90 dark:bg-stone-900/90 text-stone-700 dark:text-stone-300 hover:bg-emerald-600 hover:text-white shadow-sm'
                        }`}
                      >
                        {isSaved ? (
                          <BookmarkCheck className="w-4 h-4" />
                        ) : (
                          <Bookmark className={`w-4 h-4 ${isSaving ? 'animate-pulse' : ''}`} />
                        )}
                      </button>
                    </div>

                    {match.price_text && (
                      <div className="absolute bottom-2.5 left-2.5 px-2.5 py-1 rounded-md bg-stone-900/80 backdrop-blur-sm text-white text-xs font-black">
                        {match.price_text}
                      </div>
                    )}
                  </div>

                  {/* Card Content */}
                  <div className="p-4 space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      {getReliabilityBadge(match.source_reliability)}
                      <span className="text-[11px] font-mono font-medium text-stone-500 dark:text-stone-400 truncate max-w-[120px]">
                        {match.source_domain}
                      </span>
                    </div>

                    <div>
                      <h4 className="font-bold text-stone-900 dark:text-stone-100 text-sm line-clamp-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                        {match.title || match.detected_product_type || 'Visually Similar Garment'}
                      </h4>
                      {match.brand && (
                        <p className="text-xs text-stone-500 dark:text-stone-400 mt-0.5 font-medium">
                          Brand: <span className="font-bold text-stone-700 dark:text-stone-300">{match.brand}</span>
                        </p>
                      )}
                    </div>

                    {/* Fabric Composition Box */}
                    <div className="p-3 rounded-lg bg-white dark:bg-stone-900/80 border border-stone-200/80 dark:border-stone-700/60 text-xs">
                      {match.fabric_text_found && match.verification_status === 'source_text_found' ? (
                        <div className="space-y-1">
                          <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-bold text-[11px] uppercase tracking-wide">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Source Page States:
                          </div>
                          <p className="text-stone-800 dark:text-stone-200 font-medium italic">
                            "{match.fabric_text_found}"
                          </p>
                        </div>
                      ) : (
                        <div className="flex items-start gap-1.5 text-stone-500 dark:text-stone-400">
                          <Info className="w-3.5 h-3.5 shrink-0 mt-0.5 text-stone-400" />
                          <span className="text-[11px] leading-tight">
                            Fabric composition not verified from this web match. Always verify with product label.
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Card Footer Actions */}
                <div className="p-4 pt-0 flex items-center gap-2">
                  <a
                    href={match.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold rounded-lg bg-stone-900 hover:bg-stone-800 text-white dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-white transition-colors shadow-sm"
                  >
                    <span>Open Source</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>

                  <button
                    onClick={() => handleSave(match)}
                    disabled={isSaved || isSaving}
                    className={`inline-flex items-center justify-center gap-1 px-3 py-2 text-xs font-bold rounded-lg border transition-all ${
                      isSaved
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-700'
                        : 'bg-white dark:bg-stone-800 text-stone-700 dark:text-stone-200 border-stone-300 dark:border-stone-700 hover:bg-stone-100 dark:hover:bg-stone-700'
                    }`}
                  >
                    {isSaved ? (
                      <>
                        <BookmarkCheck className="w-3.5 h-3.5" />
                        <span>Saved</span>
                      </>
                    ) : (
                      <>
                        <Bookmark className="w-3.5 h-3.5" />
                        <span>Save</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
