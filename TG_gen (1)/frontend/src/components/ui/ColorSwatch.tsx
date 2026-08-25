import React from 'react';

interface ColorSwatchProps {
  colors: string[];
  size?: 'sm' | 'md' | 'lg';
}

export const ColorSwatch: React.FC<ColorSwatchProps> = ({ colors, size = 'md' }) => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <div className="flex items-center space-x-1.5">
      {colors.map((color, idx) => (
        <div
          key={idx}
          className={`${sizeMap[size]} rounded-full border border-white/50 shadow-sm relative group cursor-pointer`}
          style={{ backgroundColor: color }}
          title={color}
        >
          <span className="opacity-0 group-hover:opacity-100 absolute -bottom-7 left-1/2 -translate-x-1/2 bg-charcoal-900 text-white text-[10px] px-1.5 py-0.5 rounded shadow whitespace-nowrap z-10 transition-opacity">
            {color}
          </span>
        </div>
      ))}
    </div>
  );
};
