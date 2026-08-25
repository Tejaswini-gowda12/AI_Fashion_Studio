import React from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-charcoal-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-cream-200 dark:border-charcoal-700 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center pb-4 mb-4 border-b border-cream-200 dark:border-charcoal-700">
          <h3 className="font-bold text-lg text-forest-900 dark:text-cream-100">{title}</h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-sage-600 hover:bg-sage-100 dark:hover:bg-charcoal-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};
