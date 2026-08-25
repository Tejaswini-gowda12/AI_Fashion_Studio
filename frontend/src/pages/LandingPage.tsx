import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Leaf, Sliders, Droplets, ShieldCheck, ArrowRight, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden bg-gradient-to-b from-sage-100/50 via-cream-100 to-transparent dark:from-charcoal-950 dark:via-charcoal-900 dark:to-charcoal-900">
        <div className="max-w-6xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-forest-900/10 dark:bg-forest-900/40 border border-forest-900/20 text-forest-900 dark:text-sage-300 text-xs font-semibold mb-6">
            <Sparkles className="w-4 h-4 text-terracotta-500" /> AI-Driven Fashion Tech & Circular Design Platform
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-forest-900 dark:text-cream-100 tracking-tight leading-tight mb-6">
            Preserve Fashion Intent.<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-forest-700 via-forest-900 to-terracotta-500">
              Pioneer Sustainable Impact.
            </span>
          </h1>

          <p className="max-w-3xl mx-auto text-base sm:text-lg text-sage-700 dark:text-sage-300 mb-10 leading-relaxed">
            Upload inspiration garments, analyze material weaves & drape via AI Vision, receive weighted sustainable fabric recommendations, and estimate lifecycle water & carbon savings in real time.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" className="w-full sm:w-auto gap-2 shadow-lg">
                Start Design Project <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Try Demo Account
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-forest-900 dark:text-cream-100">End-to-End Circular Design Workflow</h2>
          <p className="text-sage-600 dark:text-sage-400 text-sm mt-2">Empowering eco-conscious luxury brands with data transparency.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-charcoal-800 p-6 rounded-2xl border border-cream-200 dark:border-charcoal-700 shadow-sm">
            <div className="w-12 h-12 rounded-xl bg-forest-900/10 dark:bg-forest-900/50 flex items-center justify-center text-forest-800 dark:text-sage-300 mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-forest-900 dark:text-cream-100 mb-2">1. AI Vision Material Analysis</h3>
            <p className="text-xs text-sage-600 dark:text-sage-400 leading-relaxed">
              Extract fabric characteristics—weave, drape, thickness, shine, stretch, and color palette—from reference images.
            </p>
          </div>

          <div className="bg-white dark:bg-charcoal-800 p-6 rounded-2xl border border-cream-200 dark:border-charcoal-700 shadow-sm">
            <div className="w-12 h-12 rounded-xl bg-terracotta-500/10 flex items-center justify-center text-terracotta-500 mb-4">
              <Sliders className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-forest-900 dark:text-cream-100 mb-2">2. Multi-Criteria Priority Slider</h3>
            <p className="text-xs text-sage-600 dark:text-sage-400 leading-relaxed">
              Adjust custom weights for low cost, closest appearance, low water, low carbon, recyclability, and vegan requirements.
            </p>
          </div>

          <div className="bg-white dark:bg-charcoal-800 p-6 rounded-2xl border border-cream-200 dark:border-charcoal-700 shadow-sm">
            <div className="w-12 h-12 rounded-xl bg-sage-300/20 flex items-center justify-center text-forest-900 dark:text-sage-300 mb-4">
              <Leaf className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-forest-900 dark:text-cream-100 mb-2">3. Transparent Impact Audits</h3>
            <p className="text-xs text-sage-600 dark:text-sage-400 leading-relaxed">
              Quantify water saved (Liters), CO2 reduced (kg), and non-toxic chemical reductions with downloadable PDF audit reports.
            </p>
          </div>
        </div>
      </section>

      {/* Sustainable Fiber Catalog Preview */}
      <section className="py-12 bg-sage-100/30 dark:bg-charcoal-950 px-4 sm:px-6 lg:px-8 border-t border-cream-200 dark:border-charcoal-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
          <div>
            <span className="text-xs font-semibold text-terracotta-500 uppercase tracking-wider">Curated Eco Catalog</span>
            <h2 className="text-2xl font-bold text-forest-900 dark:text-cream-100 mt-1">100% Sustainable & Regenerative Materials</h2>
            <p className="text-xs text-sage-600 dark:text-sage-400 max-w-xl mt-2">
              From GOTS Organic Cotton and Regenerative Bast Hemp to Closed-Loop Tencel Lyocell, Econyl, and Zero-Chemical Botanical Dyes.
            </p>
          </div>
          <Link to="/register">
            <Button variant="secondary" className="gap-2 shrink-0">
              Explore Material Library <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};
