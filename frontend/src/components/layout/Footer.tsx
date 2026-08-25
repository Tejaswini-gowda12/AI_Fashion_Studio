import React from 'react';
import { Leaf } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-cream-200 dark:border-charcoal-800 bg-white/60 dark:bg-charcoal-900/60 backdrop-blur-sm py-8 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-sage-600 dark:text-sage-400">
        <div className="flex items-center gap-2 font-medium">
          <Leaf className="w-4 h-4 text-forest-700 dark:text-sage-400" />
          <span>AI Sustainable Fabric Analyzer & Fashion Assistant &copy; {new Date().getFullYear()}</span>
        </div>
        <p className="text-center sm:text-right font-normal">
          Empowering designers with transparent eco-metrics, non-toxic dyes, and circular materials.
        </p>
      </div>
    </footer>
  );
};
