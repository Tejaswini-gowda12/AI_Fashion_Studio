import React from 'react';

interface SliderProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange: (value: number) => void;
  description?: string;
}

export const Slider: React.FC<SliderProps> = ({
  label,
  value,
  min = 0,
  max = 1,
  step = 0.05,
  onChange,
  description
}) => {
  const percentage = Math.round(((value - min) / (max - min)) * 100);

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center text-xs">
        <label className="font-semibold text-charcoal-800 dark:text-cream-100">{label}</label>
        <span className="font-bold text-forest-700 dark:text-sage-300">{percentage}%</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-cream-200 dark:bg-charcoal-900 rounded-lg appearance-none cursor-pointer accent-forest-700"
      />
      {description && <p className="text-[11px] text-sage-600 dark:text-sage-400">{description}</p>}
    </div>
  );
};
