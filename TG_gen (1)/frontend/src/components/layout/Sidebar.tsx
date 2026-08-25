import React from 'react';
import { NavLink } from 'react-router-dom';
import { Sparkles, Sliders, Droplets, Leaf, MessageSquare, Image, ArrowLeft, FileText } from 'lucide-react';

interface SidebarProps {
  projectId: number;
  projectTitle: string;
  hasAnalysis: boolean;
  hasFabricSelected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  projectId,
  projectTitle,
  hasAnalysis,
  hasFabricSelected
}) => {
  const steps = [
    {
      to: `/projects/${projectId}/analysis`,
      label: '1. Vision Texture Analysis',
      icon: Sparkles,
      enabled: true
    },
    {
      to: `/projects/${projectId}/recommendations`,
      label: '2. Sustainable Fabrics',
      icon: Sliders,
      enabled: hasAnalysis
    },
    {
      to: `/projects/${projectId}/dyeing`,
      label: '3. Low-Waste Dyeing',
      icon: Droplets,
      enabled: hasFabricSelected
    },
    {
      to: `/projects/${projectId}/chat`,
      label: '4. LLM Assistant & Explanations',
      icon: MessageSquare,
      enabled: true
    },
    {
      to: `/projects/${projectId}/concepts`,
      label: '5. AI Design Concepts',
      icon: Image,
      enabled: true
    },
    {
      to: `/projects/${projectId}/impact`,
      label: '6. Impact & PDF Audit Report',
      icon: FileText,
      enabled: hasFabricSelected
    }
  ];

  return (
    <aside className="w-full md:w-64 bg-white dark:bg-charcoal-800 rounded-2xl border border-cream-200 dark:border-charcoal-800 p-4 shadow-sm h-fit">
      <div className="mb-4 pb-3 border-b border-cream-200 dark:border-charcoal-800">
        <NavLink
          to="/projects"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-sage-600 dark:text-sage-400 hover:text-forest-900 transition-colors mb-2"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Projects
        </NavLink>
        <h2 className="font-bold text-base text-forest-900 dark:text-cream-100 truncate">{projectTitle}</h2>
      </div>

      <nav className="space-y-1">
        {steps.map((step) => {
          const Icon = step.icon;
          return step.enabled ? (
            <NavLink
              key={step.to}
              to={step.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-xs transition-all ${
                  isActive
                    ? 'bg-forest-900 text-cream-100 shadow-md font-semibold'
                    : 'text-charcoal-800 dark:text-cream-200 hover:bg-sage-100 dark:hover:bg-charcoal-900'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{step.label}</span>
            </NavLink>
          ) : (
            <div
              key={step.to}
              className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-xs text-stone-400 dark:text-stone-600 cursor-not-allowed opacity-60"
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{step.label}</span>
            </div>
          );
        })}
      </nav>
    </aside>
  );
};
