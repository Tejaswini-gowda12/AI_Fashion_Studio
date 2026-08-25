import React from 'react';
import { GENERATION_STEPS, GenerationStatus } from '../../types/outfit';
import { CheckCircle, Loader2, Circle } from 'lucide-react';

interface GenerationStepperProps {
  status: GenerationStatus;
}

export const GenerationStepper: React.FC<GenerationStepperProps> = ({ status }) => {
  const activeIndex = GENERATION_STEPS.findIndex(s => s.key === status);
  const isDone = status === 'done';

  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <div className="relative">
        {/* Connector line */}
        <div className="absolute top-6 left-0 right-0 h-0.5 bg-charcoal-800 dark:bg-charcoal-700" />
        <div
          className="absolute top-6 left-0 h-0.5 bg-gradient-to-r from-forest-600 to-sage-400 transition-all duration-700"
          style={{
            width: isDone
              ? '100%'
              : activeIndex >= 0
              ? `${(activeIndex / (GENERATION_STEPS.length - 1)) * 100}%`
              : '0%',
          }}
        />

        <div className="relative flex justify-between">
          {GENERATION_STEPS.map((step, idx) => {
            const isCompleted = isDone || idx < activeIndex;
            const isActive = step.key === status;

            return (
              <div key={step.key} className="flex flex-col items-center gap-2" style={{ minWidth: 0 }}>
                {/* Circle */}
                <div
                  className={`
                    relative z-10 w-12 h-12 rounded-full flex items-center justify-center
                    border-2 transition-all duration-500
                    ${isCompleted
                      ? 'bg-forest-600 border-forest-500 text-white'
                      : isActive
                      ? 'bg-forest-900 border-sage-400 text-sage-300'
                      : 'bg-charcoal-900 border-charcoal-700 text-charcoal-500'}
                  `}
                >
                  {isCompleted ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : isActive ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Circle className="w-5 h-5" />
                  )}
                </div>

                {/* Labels */}
                <div className="text-center" style={{ maxWidth: '90px' }}>
                  <p className={`text-xs font-bold truncate ${
                    isCompleted || isActive
                      ? 'text-forest-900 dark:text-sage-300'
                      : 'text-forest-700 dark:text-charcoal-400'
                  }`}>
                    {step.label}
                  </p>
                  {isActive && (
                    <p className="text-[10px] text-forest-800 dark:text-charcoal-400 mt-0.5 leading-tight font-medium">
                      {step.description}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
