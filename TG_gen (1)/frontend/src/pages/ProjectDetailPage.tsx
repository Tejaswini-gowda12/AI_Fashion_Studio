import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectService } from '../services/api';
import { Project } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { Sparkles, Sliders, Droplets, Leaf, MessageSquare, Image, ArrowRight } from 'lucide-react';

export const ProjectDetailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProject = async () => {
      if (!projectId) return;
      try {
        const res = await projectService.get(parseInt(projectId));
        setProject(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadProject();
  }, [projectId]);

  if (loading || !project) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <LoadingSkeleton />
      </div>
    );
  }

  const hasAnalysis = (project.reference_images || []).length > 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row gap-8">
        <Sidebar
          projectId={project.id}
          projectTitle={project.title}
          hasAnalysis={hasAnalysis}
          hasFabricSelected={hasAnalysis}
        />

        <main className="flex-1 space-y-6">
          <Card className="bg-gradient-to-r from-forest-900 to-forest-950 text-cream-100 p-6">
            <div className="flex items-center justify-between mb-2">
              <Badge variant="sage">{project.target_garment_type || 'Garment'}</Badge>
              <span className="text-xs text-sage-300">{project.intended_season || 'All Season'}</span>
            </div>
            <h1 className="text-2xl font-bold mb-2">{project.title}</h1>
            <p className="text-xs text-sage-200 leading-relaxed mb-4">{project.description || 'No description provided.'}</p>
            {project.sustainability_goal && (
              <div className="p-3 rounded-xl bg-cream-100/10 border border-cream-100/20 text-xs text-sage-200">
                <span className="font-bold text-amber-400 block text-[10px]">SUSTAINABILITY GOAL</span>
                {project.sustainability_goal}
              </div>
            )}
          </Card>

          <h2 className="text-lg font-bold text-forest-900 dark:text-cream-100">Project Action Workspace</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link to={`/projects/${project.id}/analysis`}>
              <Card className="hover:border-forest-700 transition-colors h-full flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-forest-900/10 dark:bg-forest-900/50 text-forest-800 dark:text-sage-300 flex items-center justify-center mb-3">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-sm text-forest-900 dark:text-cream-100 mb-1">1. AI Vision Analysis</h3>
                  <p className="text-xs text-sage-600 dark:text-sage-400">Upload garment inspiration image & extract visual texture/weave attributes.</p>
                </div>
                <div className="mt-4 pt-3 border-t border-cream-200 dark:border-charcoal-700 flex justify-end">
                  <span className="text-xs font-bold text-forest-700 dark:text-sage-300 flex items-center gap-1">Launch <ArrowRight className="w-3.5 h-3.5" /></span>
                </div>
              </Card>
            </Link>

            <Link to={`/projects/${project.id}/recommendations`}>
              <Card className="hover:border-forest-700 transition-colors h-full flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-terracotta-500/10 text-terracotta-500 flex items-center justify-center mb-3">
                    <Sliders className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-sm text-forest-900 dark:text-cream-100 mb-1">2. Sustainable Fabrics</h3>
                  <p className="text-xs text-sage-600 dark:text-sage-400">Adjust weighted sliders to evaluate matching eco fabric recommendations.</p>
                </div>
                <div className="mt-4 pt-3 border-t border-cream-200 dark:border-charcoal-700 flex justify-end">
                  <span className="text-xs font-bold text-forest-700 dark:text-sage-300 flex items-center gap-1">Launch <ArrowRight className="w-3.5 h-3.5" /></span>
                </div>
              </Card>
            </Link>

            <Link to={`/projects/${project.id}/dyeing`}>
              <Card className="hover:border-forest-700 transition-colors h-full flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center mb-3">
                    <Droplets className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-sm text-forest-900 dark:text-cream-100 mb-1">3. Low-Impact Dyeing</h3>
                  <p className="text-xs text-sage-600 dark:text-sage-400">Evaluate botanical, low-impact fiber reactive & waterless dye options.</p>
                </div>
                <div className="mt-4 pt-3 border-t border-cream-200 dark:border-charcoal-700 flex justify-end">
                  <span className="text-xs font-bold text-forest-700 dark:text-sage-300 flex items-center gap-1">Launch <ArrowRight className="w-3.5 h-3.5" /></span>
                </div>
              </Card>
            </Link>

            <Link to={`/projects/${project.id}/impact`}>
              <Card className="hover:border-forest-700 transition-colors h-full flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-sage-300/20 text-forest-900 dark:text-sage-300 flex items-center justify-center mb-3">
                    <Leaf className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-sm text-forest-900 dark:text-cream-100 mb-1">4. Impact Assessment</h3>
                  <p className="text-xs text-sage-600 dark:text-sage-400">Compare water & CO2 lifecycle savings and download PDF audit report.</p>
                </div>
                <div className="mt-4 pt-3 border-t border-cream-200 dark:border-charcoal-700 flex justify-end">
                  <span className="text-xs font-bold text-forest-700 dark:text-sage-300 flex items-center gap-1">Launch <ArrowRight className="w-3.5 h-3.5" /></span>
                </div>
              </Card>
            </Link>
          </div>
        </main>
      </div>
    </div>
  );
};
