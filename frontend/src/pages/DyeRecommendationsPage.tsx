import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { Droplets, CheckCircle2, ArrowRight, ShieldAlert } from 'lucide-react';
import { recommendationService, projectService, analysisService } from '../services/api';
import { DyeRecommendation, Project, FabricAnalysis } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { ColorSwatch } from '../components/ui/ColorSwatch';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const DyeRecommendationsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const fabricIdParam = searchParams.get('fabricId') || '1';

  const [project, setProject] = useState<Project | null>(null);
  const [analysis, setAnalysis] = useState<FabricAnalysis | null>(null);
  const [dyes, setDyes] = useState<DyeRecommendation[]>([]);
  const [selectedDyeId, setSelectedDyeId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

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

          const list = await recommendationService.getDyeRecommendations(lastAnalysis.id, parseInt(fabricIdParam));
          setDyes(list);
          if (list.length > 0) {
            setSelectedDyeId(list[0].dye_method.id);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [projectId, fabricIdParam]);

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
          hasFabricSelected={true}
        />

        <main className="flex-1 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-forest-900 dark:text-cream-100">Step 3: Low-Impact Dyeing Methods</h1>
              <p className="text-xs text-sage-600 dark:text-sage-400">Select non-toxic dyeing processes aligned with your extracted garment color palette.</p>
            </div>
            {selectedDyeId && (
              <Button
                onClick={() => navigate(`/projects/${project.id}/impact?fabricId=${fabricIdParam}&dyeId=${selectedDyeId}`)}
                className="gap-2 shrink-0"
              >
                Evaluate Environmental Impact <ArrowRight className="w-4 h-4" />
              </Button>
            )}
          </div>

          {/* Color Swatches Extracted */}
          {analysis && (
            <Card className="flex items-center justify-between bg-sage-50 dark:bg-charcoal-800 p-4 border-sage-200">
              <div>
                <span className="text-[10px] font-semibold text-sage-500 uppercase tracking-wider">Reference Color Palette</span>
                <p className="text-xs font-bold text-forest-900 dark:text-cream-100">Target Hues for Dye Matching</p>
              </div>
              <ColorSwatch colors={[...(analysis.dominant_colors || []), ...(analysis.secondary_colors || [])]} size="lg" />
            </Card>
          )}

          {/* Dye Methods Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {dyes.map((item) => {
              const isSelected = selectedDyeId === item.dye_method.id;
              return (
                <Card
                  key={item.dye_method.id}
                  className={`flex flex-col justify-between transition-all ${
                    isSelected
                      ? 'border-2 border-forest-900 dark:border-sage-400 bg-forest-50/20 dark:bg-forest-950/20 shadow-md'
                      : 'hover:border-sage-300'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge variant={isSelected ? 'forest' : 'sage'}>{item.dye_method.process_type}</Badge>
                      <span className="text-xs font-semibold text-terracotta-500">Water Impact: {item.water_impact}</span>
                    </div>

                    <h3 className="font-bold text-lg text-forest-900 dark:text-cream-100">{item.dye_method.name}</h3>
                    <p className="text-xs text-sage-600 dark:text-sage-400 leading-relaxed">{item.recommendation_rationale}</p>

                    <div className="p-3 rounded-xl bg-sage-100/50 dark:bg-charcoal-900 text-xs space-y-1">
                      <div className="flex justify-between">
                        <span className="text-sage-600">Color Accuracy:</span>
                        <span className="font-bold text-forest-800 dark:text-sage-300">{item.color_accuracy}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sage-600">Energy Consumption:</span>
                        <span className="font-bold text-forest-800 dark:text-sage-300">{item.energy_impact}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sage-600">Cost Level:</span>
                        <span className="font-bold text-terracotta-500">{item.estimated_cost}</span>
                      </div>
                    </div>

                    {item.dye_method.limitation_notes && (
                      <div className="flex items-start gap-2 p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 text-[11px] text-amber-800 dark:text-amber-300">
                        <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                        <span>{item.dye_method.limitation_notes}</span>
                      </div>
                    )}
                  </div>

                  <div className="pt-4 mt-4 border-t border-cream-200 dark:border-charcoal-700 flex justify-end">
                    <Button
                      variant={isSelected ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedDyeId(item.dye_method.id)}
                      className="gap-1.5 w-full sm:w-auto"
                    >
                      {isSelected ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : null}
                      {isSelected ? 'Selected Dye Method' : 'Select Dye Option'}
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        </main>
      </div>
    </div>
  );
};
