import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <div {...props} className={`bg-white dark:bg-charcoal-800 rounded-2xl border border-cream-200 dark:border-charcoal-800 p-6 shadow-sm hover:shadow-md transition-all ${className}`}>
      {children}
    </div>
  );
};
