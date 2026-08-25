import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  className = '',
  ...props
}) => {
  const base = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-forest-900 text-cream-100 hover:bg-forest-800 shadow-sm active:scale-[0.98]',
    secondary: 'bg-terracotta-500 text-white hover:bg-terracotta-600 shadow-sm active:scale-[0.98]',
    outline: 'border border-forest-900/30 text-forest-900 dark:text-cream-100 hover:bg-forest-900/10 dark:hover:bg-charcoal-800',
    ghost: 'text-charcoal-800 dark:text-cream-200 hover:bg-sage-100 dark:hover:bg-charcoal-800',
    danger: 'bg-rose-600 text-white hover:bg-rose-700 active:scale-[0.98]'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props}>
      {children}
    </button>
  );
};
