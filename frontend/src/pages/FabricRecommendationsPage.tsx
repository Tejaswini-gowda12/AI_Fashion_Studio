import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Sliders, Leaf, CheckCircle2, ArrowRight, RefreshCw, Info, Droplet, ShieldCheck, Award } from 'lucide-react';
import { recommendationService, projectService, analysisService } from '../services/api';
import { FabricRecommendation, PriorityWeights, Project, FabricAnalysis, Fabric } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Slider } from '../components/ui/Slider';
import { Modal } from '../components/ui/Modal';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { getClientFabricDetails } from '../services/fabricDetails';

export const FabricRecommendationsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [analysis, setAnalysis] = useState<FabricAnalysis | null>(null);
  const [recommendations, setRecommendations] = useState<FabricRecommendation[]>([]);
  const [selectedFabricId, setSelectedFabricId] = useState<number | null>(null);
  const [inspectModalFabric, setInspectModalFabric] = useState<Fabric | null>(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);

  const [weights, setWeights] = useState<PriorityWeights>({
    lowest_cost: 0.4,
    closest_appearance: 0.8,
    low_water: 0.8,
    low_carbon: 0.7,
    recyclability: 0.6,
    vegan: 0.0,
    durability: 0.6
  });

  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      if (!projectId) return;
      try {
        const proj = await projectService.get(parseInt(projectId));
        setProject(proj);

        if (proj.reference_images && proj.reference_images.length > 0) {
          const lastImg = proj.reference_images[proj.reference_images.length - 1];
          const lastAnalysis = await analysisService.get(lastImg.id);
          setAnalysis(lastAnalysis);
          fetchRecs(lastAnalysis.id, weights);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [projectId]);

  const fetchRecs = async (analysisId: number, currentWeights: PriorityWeights) => {
    setCalculating(true);
    try {
      const list = await recommendationService.getFabricRecommendations(analysisId, currentWeights);
      setRecommendations(list);
      if (list.length > 0 && !selectedFabricId) {
        setSelectedFabricId(list[0].fabric.id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setCalculating(false);
    }
  };

  const handleWeightChange = (key: keyof PriorityWeights, value: number) => {
    const newWeights = { ...weights, [key]: value };
    setWeights(newWeights);
    if (analysis) {
      fetchRecs(analysis.id, newWeights);
    }
  };

  if (loading || !project) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <LoadingSkeleton />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row gap-8">
        <Sidebar
          projectId={project.id}
          projectTitle={project.title}
          hasAnalysis={!!analysis}
          hasFabricSelected={!!selectedFabricId}
        />

        <main className="flex-1 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-forest-900 dark:text-cream-100">Step 2: Sustainable Fabric Recommendations</h1>
              <p className="text-xs text-sage-600 dark:text-sage-400">Adjust priority sliders to re-weight fabric compatibility algorithms.</p>
            </div>
            {selectedFabricId && (
              <Button
                onClick={() => navigate(`/projects/${project.id}/dyeing?fabricId=${selectedFabricId}`)}
                className="gap-2 shrink-0"
              >
                Proceed to Dyeing <ArrowRight className="w-4 h-4" />
              </Button>
            )}
          </div>

          {/* Priority Slider Controls Grid */}
          <Card className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-cream-200 dark:border-charcoal-700">
              <h3 className="font-bold text-sm text-forest-900 dark:text-cream-100 flex items-center gap-2">
                <Sliders className="w-4 h-4 text-terracotta-500" /> Multi-Criteria Priority Weights
              </h3>
              {calculating && <span className="text-xs text-sage-500 flex items-center gap-1"><RefreshCw className="w-3 h-3 animate-spin" /> Recalculating...</span>}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <Slider
                label="Lowest Cost / Economical"
                value={weights.lowest_cost}
                onChange={(v) => handleWeightChange('lowest_cost', v)}
                description="Prioritize budget-friendly raw materials"
              />
              <Slider
                label="Closest Visual Appearance"
                value={weights.closest_appearance}
                onChange={(v) => handleWeightChange('closest_appearance', v)}
                description="Match weave, drape & shine of reference photo"
              />
              <Slider
                label="Low Water Footprint"
                value={weights.low_water}
                onChange={(v) => handleWeightChange('low_water', v)}
                description="Prioritize fibers requiring minimal agricultural water"
              />
              <Slider
                label="Low Carbon Footprint"
                value={weights.low_carbon}
                onChange={(v) => handleWeightChange('low_carbon', v)}
                description="Minimize greenhouse gas emission profile"
              />
              <Slider
                label="Recyclability / Circular"
                value={weights.recyclability}
                onChange={(v) => handleWeightChange('recyclability', v)}
                description="Ensure end-of-life circular recyclability"
              />
              <Slider
                label="100% Vegan Requirement"
                value={weights.vegan}
                onChange={(v) => handleWeightChange('vegan', v)}
                description="Strictly eliminate animal-derived fibers"
              />
            </div>
          </Card>

          {/* Recommended Fabrics List */}
          <div className="space-y-4">
            <h3 className="font-bold text-base text-forest-900 dark:text-cream-100">Top Rated Sustainable Fabric Matches</h3>

            {recommendations.map((rec) => {
              const isSelected = selectedFabricId === rec.fabric.id;
              return (
                <Card
                  key={rec.fabric.id}
                  className={`transition-all ${
                    isSelected
                      ? 'border-2 border-forest-900 dark:border-sage-400 bg-forest-50/20 dark:bg-forest-950/20 shadow-md'
                      : 'hover:border-sage-300'
                  }`}
                >
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl font-black text-forest-900 dark:text-cream-100">{rec.match_percentage}% Match</span>
                        <Badge variant={isSelected ? 'forest' : 'sage'}>{rec.fabric.category}</Badge>
                        {rec.fabric.is_vegan && <Badge variant="terracotta">Vegan</Badge>}
                      </div>
                      <h4 className="font-bold text-lg text-forest-900 dark:text-cream-100">{rec.fabric.name}</h4>
                      <p className="text-xs text-sage-600 dark:text-sage-400 font-medium">Source: {rec.fabric.fiber_source}</p>

                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {rec.match_reasons.map((reason, idx) => (
                          <span key={idx} className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-sage-100 dark:bg-charcoal-700 text-forest-900 dark:text-sage-300 font-medium">
                            <CheckCircle2 className="w-3 h-3 text-forest-700" /> {reason}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row md:flex-col items-stretch md:items-end gap-3 w-full md:w-auto shrink-0 border-t md:border-t-0 border-cream-200 dark:border-charcoal-700 pt-4 md:pt-0">
                      <div className="text-right text-xs space-y-1 hidden sm:block">
                        <div className="text-sage-600">Water Score: <span className="font-bold text-forest-800 dark:text-sage-300">{rec.fabric.water_impact_score}/100</span></div>
                        <div className="text-sage-600">Carbon Score: <span className="font-bold text-forest-800 dark:text-sage-300">{rec.fabric.carbon_impact_score}/100</span></div>
                        <div className="text-sage-600">Cost Tier: <span className="font-bold text-terracotta-500">{rec.fabric.cost_level}</span></div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setInspectModalFabric(rec.fabric)}
                          className="gap-1 text-xs"
                        >
                          <Info className="w-3.5 h-3.5 text-sage-600" /> Fabric Details
                        </Button>

                        <Button
                          variant={isSelected ? 'primary' : 'outline'}
                          size="sm"
                          onClick={() => setSelectedFabricId(rec.fabric.id)}
                          className="gap-1.5 text-xs"
                        >
                          {isSelected ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : null}
                          {isSelected ? 'Selected Material' : 'Select Fabric'}
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Fabric Details Modal */}
          {inspectModalFabric && (() => {
            const spec = getClientFabricDetails(inspectModalFabric.name);
            return (
              <Modal
                isOpen={!!inspectModalFabric}
                onClose={() => setInspectModalFabric(null)}
                title={`${inspectModalFabric.name} Technical Specifications & Eco Details`}
              >
                <div className="space-y-4 text-xs sm:text-sm text-stone-800 dark:text-stone-200">
                  <div className="p-3 rounded-xl bg-forest-50 dark:bg-forest-950/40 border border-forest-200 dark:border-forest-800 space-y-1">
                    <p className="font-medium text-forest-900 dark:text-cream-100">{spec.description}</p>
                    <p className="text-[11px] text-sage-600 dark:text-sage-400">Fiber Origin: <strong>{spec.fiber_origin}</strong> | Weight: <strong>{spec.weight_gsm}</strong></p>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3 rounded-xl bg-cream-100 dark:bg-charcoal-800 border space-y-1">
                      <span className="text-[10px] uppercase font-bold text-sage-500 block">Water Footprint</span>
                      <strong className="text-sm font-bold text-forest-900 dark:text-cream-100 block">{spec.water_footprint_liters_per_kg}</strong>
                    </div>

                    <div className="p-3 rounded-xl bg-cream-100 dark:bg-charcoal-800 border space-y-1">
                      <span className="text-[10px] uppercase font-bold text-sage-500 block">Carbon Footprint</span>
                      <strong className="text-sm font-bold text-forest-900 dark:text-cream-100 block">{spec.carbon_footprint_kg_per_kg}</strong>
                    </div>

                    <div className="p-3 rounded-xl bg-cream-100 dark:bg-charcoal-800 border space-y-1">
                      <span className="text-[10px] uppercase font-bold text-sage-500 block">Biodegradable</span>
                      <strong className="text-sm font-bold text-forest-900 dark:text-cream-100 block">{spec.biodegradability_time}</strong>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="font-bold text-xs uppercase text-sage-600 block">Care & Washing Guidelines</span>
                    <p className="p-2.5 rounded-xl bg-cream-50 dark:bg-charcoal-900 border text-xs font-semibold">{spec.care_instructions}</p>
                  </div>

                  <div className="space-y-1">
                    <span className="font-bold text-xs uppercase text-sage-600 block">Certifications</span>
                    <div className="flex flex-wrap gap-1.5">
                      {spec.certifications.map((c, i) => (
                        <Badge key={i} variant="forest">{c}</Badge>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-2">
                    <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200">
                      <span className="font-bold text-xs text-emerald-800 dark:text-emerald-300 block mb-1">Pros</span>
                      <ul className="text-xs space-y-0.5 text-stone-700 dark:text-stone-300">
                        {spec.pros.map((p, i) => <li key={i}>✓ {p}</li>)}
                      </ul>
                    </div>

                    <div className="p-3 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200">
                      <span className="font-bold text-xs text-amber-800 dark:text-amber-300 block mb-1">Limitations</span>
                      <ul className="text-xs space-y-0.5 text-stone-700 dark:text-stone-300">
                        {spec.cons.map((c, i) => <li key={i}>• {c}</li>)}
                      </ul>
                    </div>
                  </div>
                </div>
              </Modal>
            );
          })()}

        </main>
      </div>
    </div>
  );
};
