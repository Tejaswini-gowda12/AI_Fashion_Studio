import React from 'react';

interface BadgeProps {
  variant?: 'forest' | 'sage' | 'terracotta' | 'cream' | 'neutral' | 'emerald';
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'forest', children, className = '' }) => {
  const styles = {
    forest: 'bg-forest-900 text-cream-100 border-forest-800',
    sage: 'bg-sage-100 text-sage-800 dark:bg-sage-900/40 dark:text-sage-300 border-sage-300 dark:border-sage-800',
    terracotta: 'bg-terracotta-50 text-terracotta-700 dark:bg-terracotta-900/30 dark:text-terracotta-300 border-terracotta-200 dark:border-terracotta-800',
    cream: 'bg-cream-200 text-forest-900 border-cream-300',
    neutral: 'bg-stone-100 dark:bg-charcoal-800 text-stone-700 dark:text-stone-300 border-stone-200 dark:border-charcoal-700',
    emerald: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800'
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[variant]} ${className}`}>
      {children}
    </span>
  );
};
