import React from 'react';

export const LoadingSkeleton: React.FC = () => {
  return (
    <div className="w-full space-y-4 animate-pulse p-4">
      <div className="h-6 bg-sage-200 dark:bg-charcoal-700 rounded-md w-1/3"></div>
      <div className="h-4 bg-sage-200 dark:bg-charcoal-700 rounded-md w-2/3"></div>
      <div className="h-48 bg-sage-200 dark:bg-charcoal-700 rounded-2xl w-full"></div>
    </div>
  );
};
