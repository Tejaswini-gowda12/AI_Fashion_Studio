import React, { useState, useMemo } from 'react';
import {
  OutfitGenerateRequest,
  STYLE_OPTIONS,
  GENDER_OPTIONS,
  SUSTAINABILITY_OPTIONS,
  WEATHER_OPTIONS,
  COLOR_PRESETS,
  FABRIC_PRESETS,
  SCENARIO_EXAMPLES,
} from '../../types/outfit';
import { Sparkles, X, ChevronDown, ChevronUp, Lightbulb, AlertTriangle, Check, ArrowRight } from 'lucide-react';

interface OutfitInputFormProps {
  onGenerate: (request: OutfitGenerateRequest) => void;
  isLoading: boolean;
}

/**
 * Detect gender-related terms in scenario text.
 * Uses strict word boundaries to avoid false substring matches.
 */
function detectScenarioGender(text: string): 'women' | 'men' | null {
  if (!text.trim()) return null;
  const lower = text.toLowerCase();

  const womenPattern = /\b(women|woman|female|ladies|lady|girl|girls|bride|bridesmaid|womens|women's)\b/i;
  const menPattern = /\b(men|man|male|gentlemen|gentleman|boy|boys|groom|groomsman|mens|men's)\b/i;

  const hasWomen = womenPattern.test(lower);
  const hasMen = menPattern.test(lower);

  if (hasWomen && !hasMen) return 'women';
  if (hasMen && !hasWomen) return 'men';
  return null;
}

export const OutfitInputForm: React.FC<OutfitInputFormProps> = ({ onGenerate, isLoading }) => {
  const [scenario, setScenario] = useState('');
  // Default gender preference to 'no_preference'
  const [gender, setGender] = useState<OutfitGenerateRequest['gender_preference']>('no_preference');
  const [hasUserSelectedGender, setHasUserSelectedGender] = useState(false);
  const [style, setStyle] = useState<OutfitGenerateRequest['style']>(undefined);
  const [budget, setBudget] = useState<number>(5000);
  const [showBudget, setShowBudget] = useState(false);
  const [isBudgetFriendly, setIsBudgetFriendly] = useState(false);
  const [budgetTier, setBudgetTier] = useState<'all' | 'budget_friendly' | 'balanced' | 'premium'>('all');
  const [size, setSize] = useState('');
  const [location, setLocation] = useState('India');
  const [weather, setWeather] = useState('');
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [selectedFabrics, setSelectedFabrics] = useState<string[]>([]);
  const [selectedSustainability, setSelectedSustainability] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [exampleVisible, setExampleVisible] = useState(false);
  const [dismissedConflict, setDismissedConflict] = useState<string | null>(null);

  // Detect scenario gender conflict
  const detectedGender = useMemo(() => detectScenarioGender(scenario), [scenario]);

  const genderConflict = useMemo(() => {
    if (!detectedGender || !gender || gender === 'no_preference' || gender === 'unisex') {
      return null;
    }
    if (detectedGender === 'women' && gender === 'men') {
      return {
        detected: 'women',
        selected: 'Men',
        suggested: 'women' as const,
        suggestedLabel: 'Women',
        message: 'Your scenario mentions women, but Men is selected. Update the preference?',
      };
    }
    if (detectedGender === 'men' && gender === 'women') {
      return {
        detected: 'men',
        selected: 'Women',
        suggested: 'men' as const,
        suggestedLabel: 'Men',
        message: 'Your scenario mentions men, but Women is selected. Update the preference?',
      };
    }
    return null;
  }, [detectedGender, gender]);

  const showConflictWarning = genderConflict && dismissedConflict !== `${genderConflict.detected}-${genderConflict.selected}`;

  const toggleColor = (color: string) => {
    setSelectedColors(prev =>
      prev.includes(color) ? prev.filter(c => c !== color) : [...prev, color].slice(0, 4)
    );
  };

  const toggleFabric = (fabric: string) => {
    setSelectedFabrics(prev =>
      prev.includes(fabric) ? prev.filter(f => f !== fabric) : [...prev, fabric].slice(0, 4)
    );
  };

  const toggleSustainability = (val: string) => {
    setSelectedSustainability(prev =>
      prev.includes(val) ? prev.filter(v => v !== val) : [...prev, val]
    );
  };

  const handleApplySuggestion = (suggested: 'women' | 'men') => {
    setGender(suggested);
    setHasUserSelectedGender(true);
  };

  const handleScenarioChange = (text: string) => {
    setScenario(text);
    setDismissedConflict(null);
    const detected = detectScenarioGender(text);
    if (detected && !hasUserSelectedGender) {
      setGender(detected);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!scenario.trim() || isLoading) return;

    const finalGender = (gender && gender !== 'no_preference')
      ? gender
      : (detectedGender || 'no_preference');

    onGenerate({
      scenario: scenario.trim(),
      gender_preference: finalGender,
      style,
      budget_inr: showBudget ? budget : (isBudgetFriendly ? 2500 : undefined),
      is_budget_friendly: isBudgetFriendly,
      budget_tier: budgetTier !== 'all' ? budgetTier : undefined,
      size: size || undefined,
      location: location || undefined,
      weather_season: weather || undefined,
      preferred_colors: selectedColors.map(c => {
        const preset = COLOR_PRESETS.find(p => p.hex === c);
        return preset ? preset.name.toLowerCase() : c;
      }),
      preferred_fabrics: selectedFabrics,
      sustainability_preferences: selectedSustainability,
    });
  };

  const handleSelectBudgetTier = (tier: 'budget_friendly' | 'balanced' | 'premium' | 'all') => {
    setBudgetTier(tier);
    if (tier === 'budget_friendly') {
      setShowBudget(true);
      setBudget(2500);
      setIsBudgetFriendly(true);
    } else if (tier === 'balanced') {
      setShowBudget(true);
      setBudget(5000);
      setIsBudgetFriendly(false);
    } else if (tier === 'premium') {
      setShowBudget(true);
      setBudget(12000);
      setIsBudgetFriendly(false);
    } else {
      setShowBudget(false);
      setIsBudgetFriendly(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Scenario input */}
      <div>
        <label htmlFor="outfit-scenario-input" className="block text-sm font-bold text-forest-950 dark:text-cream-100 mb-2">
          Describe your occasion or scenario <span className="text-rose-500">*</span>
        </label>
        <div className="relative">
          <textarea
            id="outfit-scenario-input"
            value={scenario}
            onChange={e => handleScenarioChange(e.target.value)}
            placeholder="e.g. I need a sustainable outfit for a college farewell party…"
            rows={3}
            maxLength={500}
            className="w-full px-4 py-3 rounded-xl bg-forest-50/40 dark:bg-charcoal-800 border border-forest-200 dark:border-charcoal-700 text-forest-950 dark:text-cream-100 placeholder-forest-700/60 resize-none focus:outline-none focus:ring-2 focus:ring-forest-500 focus:border-transparent transition text-sm font-medium"
          />
          <span className="absolute bottom-2 right-3 text-[10px] text-forest-700 dark:text-charcoal-400 font-semibold">{scenario.length}/500</span>
        </div>

        {/* Example prompts */}
        <button
          type="button"
          onClick={() => setExampleVisible(v => !v)}
          className="mt-1.5 flex items-center gap-1 text-xs text-forest-700 dark:text-sage-400 hover:underline font-bold"
        >
          <Lightbulb className="w-3.5 h-3.5" /> Try an example scenario
        </button>
        {exampleVisible && (
          <div className="mt-2 flex flex-col gap-1.5">
            {SCENARIO_EXAMPLES.map(ex => (
              <button
                key={ex}
                type="button"
                onClick={() => {
                  handleScenarioChange(ex);
                  setExampleVisible(false);
                }}
                className="text-left text-xs px-3 py-2 rounded-lg bg-forest-50 dark:bg-charcoal-800 text-forest-950 dark:text-sage-300 hover:bg-forest-100 dark:hover:bg-charcoal-700 border border-forest-200 dark:border-charcoal-700 transition font-medium"
              >
                {ex}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Gender / Style Preference */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-xs font-bold text-forest-900 dark:text-cream-300 uppercase tracking-wide">
            Gender / Fit Preference
          </label>
          {gender && (
            <span className="text-[11px] font-bold text-forest-700 dark:text-sage-400">
              Selected: {GENDER_OPTIONS.find(o => o.value === gender)?.label}
            </span>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          {GENDER_OPTIONS.map(opt => {
            const isSelected = gender === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  setGender(opt.value as any);
                  setHasUserSelectedGender(true);
                  setDismissedConflict(null);
                }}
                className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border ${
                  isSelected
                    ? 'bg-forest-700 text-cream-100 border-forest-600 shadow-sm'
                    : 'bg-cream-100 dark:bg-charcoal-800 text-charcoal-700 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-forest-400 dark:hover:border-forest-600'
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>

        {/* Conflict Warning Banner */}
        {showConflictWarning && (
          <div className="mt-3 p-3 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs animate-fadeSlideUp">
            <div className="flex items-start gap-2 text-amber-900 dark:text-amber-200">
              <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <span>{genderConflict.message}</span>
            </div>
            <div className="flex items-center gap-2 self-end sm:self-auto">
              <button
                type="button"
                onClick={() => handleApplySuggestion(genderConflict.suggested)}
                className="px-2.5 py-1 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold text-[11px] shadow-sm transition"
              >
                Update to {genderConflict.suggestedLabel}
              </button>
              <button
                type="button"
                onClick={() => setDismissedConflict(`${genderConflict.detected}-${genderConflict.selected}`)}
                className="px-2 py-1 text-charcoal-500 dark:text-charcoal-400 hover:text-charcoal-700 dark:hover:text-cream-200 text-[11px]"
              >
                Keep {genderConflict.selected}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Style selector */}
      <div>
        <label className="block text-xs font-semibold text-charcoal-600 dark:text-cream-300 mb-2 uppercase tracking-wide">
          Style Aesthetic
        </label>
        <div className="flex flex-wrap gap-2">
          {STYLE_OPTIONS.map(opt => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setStyle(prev => prev === opt.value ? undefined : opt.value as any)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border flex items-center gap-1.5 ${
                style === opt.value
                  ? 'bg-forest-700 text-cream-100 border-forest-600 shadow-sm'
                  : 'bg-cream-100 dark:bg-charcoal-800 text-charcoal-700 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-forest-400'
              }`}
            >
              <span>{opt.icon}</span> {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Sustainability Priorities */}
      <div>
        <label className="block text-xs font-semibold text-charcoal-600 dark:text-cream-300 mb-2 uppercase tracking-wide">
          Sustainability Priorities
        </label>
        <div className="flex flex-wrap gap-2">
          {SUSTAINABILITY_OPTIONS.map(opt => {
            const active = selectedSustainability.includes(opt.value);
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => toggleSustainability(opt.value)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition border ${
                  active
                    ? 'text-charcoal-900 dark:text-cream-100 font-semibold'
                    : 'bg-cream-100 dark:bg-charcoal-800 text-charcoal-600 dark:text-cream-300 border-cream-200 dark:border-charcoal-700'
                }`}
                style={active ? {
                  backgroundColor: opt.color + '25',
                  borderColor: opt.color,
                  color: opt.color,
                } : {}}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Budget & Budget-Friendly Options */}
      <div className="p-4 rounded-2xl bg-cream-50 dark:bg-charcoal-800/70 border border-cream-200 dark:border-charcoal-700 space-y-3.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-bold">
              💰
            </span>
            <div>
              <label className="text-xs font-bold text-forest-950 dark:text-cream-100 uppercase tracking-wide">
                Budget & Value Optimization
              </label>
              <p className="text-[11px] text-charcoal-500 dark:text-cream-300 font-medium">
                Choose a pricing tier or enable budget-friendly priority
              </p>
            </div>
          </div>
          {showBudget && (
            <span className="text-sm font-extrabold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              ₹{budget.toLocaleString('en-IN')}
            </span>
          )}
        </div>

        {/* Quick Budget Tiers */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <button
            type="button"
            onClick={() => handleSelectBudgetTier('budget_friendly')}
            className={`px-3 py-2 rounded-xl text-xs font-bold transition flex flex-col items-center gap-0.5 border ${
              budgetTier === 'budget_friendly'
                ? 'bg-emerald-600 text-white border-emerald-500 shadow-sm'
                : 'bg-white dark:bg-charcoal-900 text-charcoal-700 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-emerald-500/50'
            }`}
          >
            <span className="flex items-center gap-1 text-[11px]">🏷️ Budget-Friendly</span>
            <span className="text-[10px] opacity-80">&lt; ₹2,500</span>
          </button>

          <button
            type="button"
            onClick={() => handleSelectBudgetTier('balanced')}
            className={`px-3 py-2 rounded-xl text-xs font-bold transition flex flex-col items-center gap-0.5 border ${
              budgetTier === 'balanced'
                ? 'bg-forest-700 text-white border-forest-600 shadow-sm'
                : 'bg-white dark:bg-charcoal-900 text-charcoal-700 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-forest-500/50'
            }`}
          >
            <span className="flex items-center gap-1 text-[11px]">⚖️ Mid-Range</span>
            <span className="text-[10px] opacity-80">₹2.5k – ₹6k</span>
          </button>

          <button
            type="button"
            onClick={() => handleSelectBudgetTier('premium')}
            className={`px-3 py-2 rounded-xl text-xs font-bold transition flex flex-col items-center gap-0.5 border ${
              budgetTier === 'premium'
                ? 'bg-amber-700 text-white border-amber-600 shadow-sm'
                : 'bg-white dark:bg-charcoal-900 text-charcoal-700 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-amber-500/50'
            }`}
          >
            <span className="flex items-center gap-1 text-[11px]">✨ Premium Eco</span>
            <span className="text-[10px] opacity-80">₹6,000+</span>
          </button>

          <button
            type="button"
            onClick={() => handleSelectBudgetTier('all')}
            className={`px-3 py-2 rounded-xl text-xs font-bold transition flex flex-col items-center gap-0.5 border ${
              budgetTier === 'all' && !showBudget
                ? 'bg-charcoal-800 text-white border-charcoal-700 shadow-sm'
                : 'bg-white dark:bg-charcoal-900 text-charcoal-700 dark:text-cream-200 border-cream-200 dark:border-charcoal-700 hover:border-charcoal-500'
            }`}
          >
            <span className="flex items-center gap-1 text-[11px]">🌐 Any Budget</span>
            <span className="text-[10px] opacity-80">No Limit</span>
          </button>
        </div>

        {/* 1-Click Budget-Friendly Priority Toggle */}
        <div
          onClick={() => {
            const nextVal = !isBudgetFriendly;
            setIsBudgetFriendly(nextVal);
            if (nextVal) {
              setShowBudget(true);
              setBudget(prev => (prev > 3000 ? 2500 : prev));
              setBudgetTier('budget_friendly');
            }
          }}
          className={`p-2.5 rounded-xl border flex items-center justify-between cursor-pointer select-none transition ${
            isBudgetFriendly
              ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-950 dark:text-emerald-200'
              : 'bg-white/60 dark:bg-charcoal-900/60 border-cream-200 dark:border-charcoal-700 hover:border-emerald-500/30 text-charcoal-700 dark:text-cream-300'
          }`}
        >
          <div className="flex items-center gap-2">
            <span className="text-base">💸</span>
            <div>
              <p className="text-xs font-bold leading-tight">
                Budget-Friendly Priority Mode
              </p>
              <p className="text-[10px] text-charcoal-500 dark:text-cream-300 leading-tight">
                Prioritizes affordable certified fabrics, high-discount store deals & lowest cost picks.
              </p>
            </div>
          </div>
          <div className={`w-8 h-4.5 rounded-full relative transition-colors ${isBudgetFriendly ? 'bg-emerald-500' : 'bg-charcoal-500'}`}>
            <div className={`w-3.5 h-3.5 rounded-full bg-white absolute top-0.5 transition-transform ${isBudgetFriendly ? 'left-4' : 'left-0.5'}`} />
          </div>
        </div>

        {/* Custom Slider Toggle */}
        <div className="pt-2 border-t border-cream-200 dark:border-charcoal-700">
          <div className="flex items-center justify-between mb-1.5">
            <label
              className="text-[11px] font-bold text-charcoal-600 dark:text-cream-300 flex items-center gap-1.5 cursor-pointer select-none"
              onClick={() => setShowBudget(v => !v)}
            >
              <input
                type="checkbox"
                checked={showBudget}
                onChange={e => setShowBudget(e.target.checked)}
                className="rounded text-forest-600 focus:ring-forest-500"
              />
              Set custom price limit slider
            </label>
          </div>

          {showBudget && (
            <div className="animate-fadeSlideUp pt-1">
              <input
                type="range"
                min={500}
                max={50000}
                step={500}
                value={budget}
                onChange={e => setBudget(Number(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-charcoal-400 font-semibold mt-1">
                <span>₹500 (Budget)</span>
                <span>₹25,000</span>
                <span>₹50,000+</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Advanced Filters */}
      <div>
        <button
          type="button"
          onClick={() => setShowAdvanced(v => !v)}
          className="flex items-center gap-2 text-xs font-semibold text-charcoal-500 dark:text-charcoal-400 hover:text-forest-600 dark:hover:text-sage-300 transition"
        >
          {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          {showAdvanced ? 'Hide additional filters' : 'More filters (Size, Location, Colors, Fabrics)'}
        </button>

        {showAdvanced && (
          <div className="mt-3 space-y-4 p-4 rounded-2xl bg-cream-50 dark:bg-charcoal-800/50 border border-cream-200 dark:border-charcoal-700 animate-fadeSlideUp">
            {/* Size & Location */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-charcoal-700 dark:text-cream-300 mb-1">
                  Size Preference
                </label>
                <select
                  value={size}
                  onChange={e => setSize(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-white dark:bg-charcoal-800 border border-cream-200 dark:border-charcoal-700 text-sm text-charcoal-800 dark:text-cream-100 focus:outline-none focus:ring-1 focus:ring-forest-500"
                >
                  <option value="">Any Size</option>
                  {['XS','S','M','L','XL','XXL','28','30','32','34','36'].map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-charcoal-700 dark:text-cream-300 mb-1">
                  Location / Country
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={e => setLocation(e.target.value)}
                  placeholder="India"
                  className="w-full px-3 py-2 rounded-lg bg-white dark:bg-charcoal-800 border border-cream-200 dark:border-charcoal-700 text-sm text-charcoal-800 dark:text-cream-100 focus:outline-none focus:ring-1 focus:ring-forest-500"
                />
              </div>
            </div>

            {/* Weather */}
            <div>
              <label className="block text-xs font-medium text-charcoal-700 dark:text-cream-300 mb-1.5">
                Season / Weather
              </label>
              <div className="flex flex-wrap gap-1.5">
                {WEATHER_OPTIONS.map(w => (
                  <button
                    key={w}
                    type="button"
                    onClick={() => setWeather(prev => prev === w ? '' : w)}
                    className={`px-2.5 py-1 rounded-full text-xs font-medium transition border ${
                      weather === w
                        ? 'bg-sky-700 text-sky-100 border-sky-600'
                        : 'bg-white dark:bg-charcoal-800 text-charcoal-600 dark:text-cream-300 border-cream-200 dark:border-charcoal-700'
                    }`}
                  >
                    {w}
                  </button>
                ))}
              </div>
            </div>

            {/* Color Palette */}
            <div>
              <label className="block text-xs font-medium text-charcoal-700 dark:text-cream-300 mb-1.5">
                Preferred Colors <span className="text-charcoal-400">(select up to 4)</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {COLOR_PRESETS.map(c => {
                  const isPicked = selectedColors.includes(c.hex);
                  return (
                    <button
                      key={c.hex}
                      type="button"
                      onClick={() => toggleColor(c.hex)}
                      title={c.name}
                      className={`w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 ${
                        isPicked ? 'border-white scale-110 ring-2 ring-forest-500' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: c.hex }}
                    />
                  );
                })}
              </div>
              {selectedColors.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {selectedColors.map(hex => {
                    const preset = COLOR_PRESETS.find(p => p.hex === hex);
                    return (
                      <span key={hex} className="flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-cream-100 dark:bg-charcoal-700 text-charcoal-700 dark:text-cream-200 border border-cream-200 dark:border-charcoal-600">
                        <span className="w-3 h-3 rounded-full inline-block" style={{ backgroundColor: hex }} />
                        {preset?.name || hex}
                        <X className="w-3 h-3 cursor-pointer" onClick={() => toggleColor(hex)} />
                      </span>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Fabrics */}
            <div>
              <label className="block text-xs font-medium text-charcoal-700 dark:text-cream-300 mb-1.5">
                Preferred Fabrics <span className="text-charcoal-400">(select up to 4)</span>
              </label>
              <div className="flex flex-wrap gap-1.5">
                {FABRIC_PRESETS.map(f => {
                  const isPicked = selectedFabrics.includes(f);
                  return (
                    <button
                      key={f}
                      type="button"
                      onClick={() => toggleFabric(f)}
                      className={`px-2.5 py-1 rounded-full text-xs font-medium border transition ${
                        isPicked
                          ? 'bg-terracotta-100 dark:bg-terracotta-900/40 text-terracotta-700 dark:text-terracotta-300 border-terracotta-400'
                          : 'bg-white dark:bg-charcoal-800 text-charcoal-600 dark:text-cream-300 border-cream-200 dark:border-charcoal-700'
                      }`}
                    >
                      {f}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Submit Button */}
      <button
        id="generate-outfit-btn"
        type="submit"
        disabled={!scenario.trim() || isLoading}
        className="w-full py-4 rounded-2xl bg-gradient-to-r from-forest-700 to-forest-500 hover:from-forest-600 hover:to-forest-400 text-cream-100 font-bold text-base tracking-wide shadow-lg shadow-forest-900/30 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <Sparkles className="w-5 h-5" />
        {isLoading ? 'Generating Outfit Concept…' : '✨ Generate My Outfit'}
      </button>
    </form>
  );
};
