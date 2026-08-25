import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Search, FolderKanban, Copy, Trash2, ArrowRight } from 'lucide-react';
import { projectService } from '../services/api';
import { Project } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [garmentType, setGarmentType] = useState('Structured Blazer');
  const [season, setSeason] = useState('Autumn/Winter');
  const [budget, setBudget] = useState('Medium');
  const [sustainabilityGoal, setSustainabilityGoal] = useState('Reduce water footprint by 60% and use non-toxic dyes.');

  const navigate = useNavigate();

  const loadProjects = async () => {
    try {
      const list = await projectService.list();
      setProjects(list);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newProj = await projectService.create({
        title,
        description,
        target_garment_type: garmentType,
        intended_season: season,
        budget_range: budget,
        sustainability_goal: sustainabilityGoal
      });
      setIsCreateModalOpen(false);
      setTitle('');
      setDescription('');
      navigate(`/projects/${newProj.id}/analysis`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDuplicate = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await projectService.duplicate(id);
      loadProjects();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this project?')) return;
    try {
      await projectService.delete(id);
      loadProjects();
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = projects.filter(p =>
    p.title.toLowerCase().includes(search.toLowerCase()) ||
    (p.target_garment_type || '').toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <LoadingSkeleton />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-forest-900 dark:text-cream-100">Fashion Design Projects</h1>
          <p className="text-xs text-sage-600 dark:text-sage-400">Manage your collections, reference images, and eco-audits</p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)} className="gap-2 shrink-0">
          <Plus className="w-4 h-4" /> New Design Project
        </Button>
      </div>

      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-sage-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search projects by title or garment type..."
          className="w-full pl-10 pr-4 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-white dark:bg-charcoal-800 text-xs focus:outline-none focus:ring-2 focus:ring-forest-900 dark:focus:ring-sage-400"
        />
      </div>

      {filtered.length === 0 ? (
        <Card className="text-center py-12">
          <FolderKanban className="w-10 h-10 text-sage-400 mx-auto mb-2" />
          <p className="text-sm font-semibold text-forest-900 dark:text-cream-100">No matching projects found</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((project) => (
            <Card key={project.id} className="flex flex-col justify-between hover:border-forest-700 transition-colors">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="sage">{project.target_garment_type || 'Garment'}</Badge>
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={(e) => handleDuplicate(project.id, e)}
                      className="p-1 rounded text-sage-500 hover:text-forest-900 hover:bg-sage-100 dark:hover:bg-charcoal-700 transition-colors"
                      title="Duplicate project"
                    >
                      <Copy className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={(e) => handleDelete(project.id, e)}
                      className="p-1 rounded text-sage-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
                      title="Delete project"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <h3 className="font-bold text-base text-forest-900 dark:text-cream-100 mb-1">{project.title}</h3>
                <p className="text-xs text-sage-600 dark:text-sage-400 line-clamp-2 mb-3">{project.description || 'No description'}</p>

                {project.sustainability_goal && (
                  <div className="p-2.5 rounded-xl bg-sage-50 dark:bg-charcoal-900/60 border border-sage-200 dark:border-charcoal-700 text-[11px] text-forest-900 dark:text-sage-300 mb-4">
                    <span className="font-semibold block text-[10px] text-terracotta-500">ECO GOAL</span>
                    {project.sustainability_goal}
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-cream-200 dark:border-charcoal-700 flex items-center justify-between">
                <span className="text-[10px] font-semibold text-sage-500">{project.intended_season || 'All Season'}</span>
                <Link to={`/projects/${project.id}/analysis`}>
                  <Button variant="primary" size="sm" className="gap-1 text-xs">
                    Workspace <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Project Modal */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Create New Sustainable Fashion Project">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Project Title</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Organic Linen Summer Collection"
              className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-xs focus:outline-none focus:ring-2 focus:ring-forest-900"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              placeholder="Target silhouette, design inspiration, target eco benchmarks..."
              className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-xs focus:outline-none focus:ring-2 focus:ring-forest-900"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Target Garment Type</label>
              <select
                value={garmentType}
                onChange={(e) => setGarmentType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-xs"
              >
                <option value="Structured Blazer">Structured Blazer</option>
                <option value="Casual T-Shirt">Casual T-Shirt</option>
                <option value="Denim Jacket">Denim Jacket</option>
                <option value="Summer Dress">Summer Dress</option>
                <option value="Knit Sweater">Knit Sweater</option>
                <option value="Activewear Legging">Activewear Legging</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Intended Season</label>
              <select
                value={season}
                onChange={(e) => setSeason(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-xs"
              >
                <option value="Spring/Summer">Spring/Summer</option>
                <option value="Autumn/Winter">Autumn/Winter</option>
                <option value="Resort/Cruisewear">Resort/Cruisewear</option>
                <option value="All Season">All Season</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Sustainability Goal</label>
            <input
              type="text"
              value={sustainabilityGoal}
              onChange={(e) => setSustainabilityGoal(e.target.value)}
              placeholder="e.g., 100% GOTS certified fibers and zero toxic dyes"
              className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-xs"
            />
          </div>

          <div className="pt-4 flex justify-end space-x-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm">
              Create & Launch Workspace
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
