import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Leaf, FolderKanban, Droplets, Sparkles, Plus, ArrowRight, ShieldCheck, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { projectService } from '../services/api';
import { Project } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const list = await projectService.list();
        setProjects(list);
      } catch (err) {
        console.error('Failed to load projects:', err);
      } finally {
        setLoading(false);
      }
    };
    loadProjects();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <LoadingSkeleton />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-forest-900 via-forest-800 to-forest-950 rounded-3xl p-8 text-cream-100 shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cream-100/10 text-sage-300 text-xs font-semibold mb-4 border border-cream-100/20">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Fashion Designer Dashboard
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">Welcome back, {user?.full_name}!</h1>
          <p className="text-sm text-sage-200 mt-2 leading-relaxed">
            Analyze reference garments, evaluate transparent fiber & dye alternatives, and optimize your collection's environmental footprint.
          </p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Link to="/projects">
              <Button variant="secondary" className="gap-2 text-xs py-2.5">
                <Plus className="w-4 h-4" /> Start New Design Project
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Sustainability Eco Impact Overview Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="flex items-center space-x-4 border-sage-200">
          <div className="p-3 rounded-2xl bg-forest-900/10 dark:bg-forest-900/50 text-forest-800 dark:text-sage-300">
            <FolderKanban className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-sage-600 dark:text-sage-400">Active Projects</p>
            <p className="text-2xl font-bold text-forest-900 dark:text-cream-100">{projects.length}</p>
          </div>
        </Card>

        <Card className="flex items-center space-x-4 border-sage-200">
          <div className="p-3 rounded-2xl bg-blue-500/10 text-blue-600 dark:text-blue-400">
            <Droplets className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-sage-600 dark:text-sage-400">Est. Water Saved</p>
            <p className="text-2xl font-bold text-forest-900 dark:text-cream-100">4,650 L</p>
          </div>
        </Card>

        <Card className="flex items-center space-x-4 border-sage-200">
          <div className="p-3 rounded-2xl bg-terracotta-500/10 text-terracotta-500">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-sage-600 dark:text-sage-400">CO2 Emissions Avoided</p>
            <p className="text-2xl font-bold text-forest-900 dark:text-cream-100">18.4 kg</p>
          </div>
        </Card>

        <Card className="flex items-center space-x-4 border-sage-200">
          <div className="p-3 rounded-2xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
            <Leaf className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-sage-600 dark:text-sage-400">Eco Fiber Ratio</p>
            <p className="text-2xl font-bold text-forest-900 dark:text-cream-100">92.5%</p>
          </div>
        </Card>
      </div>

      {/* Recent Projects List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-forest-900 dark:text-cream-100">Recent Design Projects</h2>
          <Link to="/projects" className="text-xs font-bold text-forest-700 dark:text-sage-300 hover:underline flex items-center gap-1">
            View All ({projects.length}) <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {projects.length === 0 ? (
          <Card className="text-center py-12">
            <FolderKanban className="w-12 h-12 text-sage-400 mx-auto mb-3" />
            <h3 className="font-bold text-base text-forest-900 dark:text-cream-100">No Projects Created Yet</h3>
            <p className="text-xs text-sage-600 dark:text-sage-400 mt-1 max-w-md mx-auto mb-4">
              Create your first fashion project to analyze inspiration images and generate low-impact garment concepts.
            </p>
            <Link to="/projects">
              <Button size="sm" className="gap-2">
                <Plus className="w-4 h-4" /> Create First Project
              </Button>
            </Link>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.slice(0, 6).map((project) => (
              <Card key={project.id} className="flex flex-col justify-between hover:border-forest-700 transition-colors">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="sage">{project.target_garment_type || 'Garment'}</Badge>
                    <span className="text-[10px] text-sage-500">{new Date(project.updated_at).toLocaleDateString()}</span>
                  </div>
                  <h3 className="font-bold text-base text-forest-900 dark:text-cream-100 mb-1">{project.title}</h3>
                  <p className="text-xs text-sage-600 dark:text-sage-400 line-clamp-2 mb-4">{project.description || 'No description provided.'}</p>
                </div>
                <div className="pt-4 border-t border-cream-200 dark:border-charcoal-700 flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-terracotta-500">{project.intended_season || 'All Season'}</span>
                  <Link to={`/projects/${project.id}/analysis`}>
                    <Button variant="outline" size="sm" className="gap-1.5 text-xs">
                      Open Workspace <ArrowRight className="w-3.5 h-3.5" />
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
