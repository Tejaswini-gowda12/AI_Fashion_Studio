import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Upload, Sparkles, Check, Edit2, ArrowRight, Layers, FileText } from 'lucide-react';
import { analysisService, projectService } from '../services/api';
import { FabricAnalysis, Project } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { ColorSwatch } from '../components/ui/ColorSwatch';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const AnalysisWorkspacePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [analysis, setAnalysis] = useState<FabricAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const [isEditing, setIsEditing] = useState(false);
  const [garmentCategory, setGarmentCategory] = useState('');
  const [fabricType, setFabricType] = useState('');
  const [weave, setWeave] = useState('');
  const [thickness, setThickness] = useState('');
  const [drape, setDrape] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      if (!projectId) return;
      try {
        const proj = await projectService.get(parseInt(projectId));
        setProject(proj);

        if (proj.reference_images && proj.reference_images.length > 0) {
          const lastImg = proj.reference_images[proj.reference_images.length - 1];
          try {
            const lastAnalysis = await analysisService.get(lastImg.id);
            setAnalysis(lastAnalysis);
            initEditForm(lastAnalysis);
          } catch (e) {
            console.log('No existing analysis yet');
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [projectId]);

  const initEditForm = (data: FabricAnalysis) => {
    setGarmentCategory(data.garment_category);
    setFabricType(data.fabric_type);
    setWeave(data.weave);
    setThickness(data.thickness);
    setDrape(data.drape);
  };

  const handleFileUpload = async (file: File) => {
    if (!projectId) return;
    setAnalyzing(true);
    try {
      const res = await analysisService.uploadAndAnalyze(parseInt(projectId), file);
      setAnalysis(res);
      initEditForm(res);
      const updatedProj = await projectService.get(parseInt(projectId));
      setProject(updatedProj);
    } catch (err) {
      console.error(err);
      alert('Failed to analyze image. Please ensure file is an image (JPG/PNG).');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleSaveCorrection = async () => {
    if (!analysis) return;
    try {
      const updated = await analysisService.update(analysis.id, {
        garment_category: garmentCategory,
        fabric_type: fabricType,
        weave: weave,
        thickness: thickness,
        drape: drape
      });
      setAnalysis(updated);
      setIsEditing(false);
    } catch (err) {
      console.error(err);
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
          hasFabricSelected={!!analysis}
        />

        <main className="flex-1 space-y-6">
          {/* PDF System Architecture Flowchart Visual Banner */}
          <div className="p-4 rounded-2xl bg-gradient-to-r from-forest-950 via-forest-900 to-forest-950 text-cream-100 shadow-md">
            <div className="flex items-center gap-2 mb-3">
              <Layers className="w-4 h-4 text-terracotta-400" />
              <span className="text-xs font-bold tracking-wide uppercase text-sage-300">System Flowchart Execution Progress</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 text-[11px]">
              <div className="p-2 rounded-xl bg-cream-100/10 border border-cream-100/20 text-center font-bold text-emerald-300">
                1. Image Upload
              </div>
              <div className="p-2 rounded-xl bg-cream-100/10 border border-cream-100/20 text-center font-semibold text-cream-200">
                2. Vision Transformer
              </div>
              <div className="p-2 rounded-xl bg-cream-100/10 border border-cream-100/20 text-center font-semibold text-cream-200">
                3. Material ID
              </div>
              <div className="p-2 rounded-xl bg-cream-100/10 border border-cream-100/20 text-center font-semibold text-cream-200">
                4. Eco Fabrics
              </div>
              <div className="p-2 rounded-xl bg-cream-100/10 border border-cream-100/20 text-center font-semibold text-cream-200">
                5. Low-Impact Dyes
              </div>
              <div className="p-2 rounded-xl bg-cream-100/10 border border-cream-100/20 text-center font-semibold text-cream-200">
                6. LLM & Audit PDF
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-forest-900 dark:text-cream-100">Step 1: Upload & Fabric Texture Analysis</h1>
              <p className="text-xs text-sage-600 dark:text-sage-400">Upload garment inspiration images to extract texture, weave, and drape attributes.</p>
            </div>
            {analysis && (
              <Button onClick={() => navigate(`/projects/${project.id}/recommendations`)} className="gap-2 shrink-0">
                Recommend Sustainable Fabrics <ArrowRight className="w-4 h-4" />
              </Button>
            )}
          </div>

          {/* Upload Dropzone */}
          <Card
            className={`border-2 border-dashed transition-all text-center p-8 ${
              dragOver
                ? 'border-forest-900 bg-forest-50/50 dark:bg-forest-950/50'
                : 'border-cream-300 dark:border-charcoal-700 bg-cream-50/50 dark:bg-charcoal-900/50'
            }`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            {analyzing ? (
              <div className="py-8 space-y-3">
                <div className="w-12 h-12 rounded-full border-4 border-forest-900 border-t-transparent animate-spin mx-auto"></div>
                <h3 className="font-bold text-base text-forest-900 dark:text-cream-100">Processing & Analyzing Vision Attributes...</h3>
                <p className="text-xs text-sage-600 dark:text-sage-400">Extracting weave, opacity, drape, thickness, and color swatches...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-forest-900/10 text-forest-800 dark:text-sage-300 flex items-center justify-center mx-auto">
                  <Upload className="w-7 h-7" />
                </div>
                <div>
                  <p className="text-sm font-bold text-forest-900 dark:text-cream-100">Drag & drop inspiration garment photo here</p>
                  <p className="text-xs text-sage-500 mt-1">Supports JPG, PNG, WebP up to 10MB</p>
                </div>
                <label className="inline-block">
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) handleFileUpload(e.target.files[0]);
                    }}
                  />
                  <span className="px-4 py-2 rounded-xl bg-forest-900 text-cream-100 text-xs font-semibold hover:bg-forest-800 cursor-pointer shadow-sm">
                    Browse Computer Files
                  </span>
                </label>
              </div>
            )}
          </Card>

          {/* Analysis Results Display */}
          {analysis && (
            <Card className="space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-cream-200 dark:border-charcoal-700">
                <div className="flex items-center space-x-3">
                  <Badge variant="forest">Confidence Score: {Math.round(analysis.confidence_score * 100)}%</Badge>
                  {analysis.is_user_corrected && <Badge variant="terracotta">User Corrected</Badge>}
                </div>
                <Button variant="outline" size="sm" onClick={() => setIsEditing(!isEditing)} className="gap-1.5 text-xs">
                  <Edit2 className="w-3.5 h-3.5" /> {isEditing ? 'Cancel Edit' : 'Correct Attributes'}
                </Button>
              </div>

              {isEditing ? (
                <div className="space-y-4 p-4 rounded-xl bg-cream-50 dark:bg-charcoal-900 border border-cream-300 dark:border-charcoal-700">
                  <h4 className="font-bold text-sm text-forest-900 dark:text-cream-100">Manual Attribute Correction</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold mb-1">Garment Category</label>
                      <input
                        type="text"
                        value={garmentCategory}
                        onChange={(e) => setGarmentCategory(e.target.value)}
                        className="w-full px-3 py-1.5 rounded-lg border text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1">Fabric Type</label>
                      <input
                        type="text"
                        value={fabricType}
                        onChange={(e) => setFabricType(e.target.value)}
                        className="w-full px-3 py-1.5 rounded-lg border text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1">Weave / Texture</label>
                      <input
                        type="text"
                        value={weave}
                        onChange={(e) => setWeave(e.target.value)}
                        className="w-full px-3 py-1.5 rounded-lg border text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1">Thickness</label>
                      <input
                        type="text"
                        value={thickness}
                        onChange={(e) => setThickness(e.target.value)}
                        className="w-full px-3 py-1.5 rounded-lg border text-xs"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <Button size="sm" onClick={handleSaveCorrection} className="gap-1 text-xs">
                      <Check className="w-3.5 h-3.5" /> Save Attributes
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                  <div className="p-4 rounded-xl bg-sage-50 dark:bg-charcoal-900/50 border border-sage-200 dark:border-charcoal-700">
                    <span className="text-[10px] font-semibold text-sage-500 uppercase tracking-wider">Garment Category</span>
                    <p className="font-bold text-base text-forest-900 dark:text-cream-100 mt-1">{analysis.garment_category}</p>
                    <span className="text-xs text-sage-600 dark:text-sage-400 mt-1 block">Baseline Fabric: {analysis.fabric_type}</span>
                  </div>

                  <div className="p-4 rounded-xl bg-sage-50 dark:bg-charcoal-900/50 border border-sage-200 dark:border-charcoal-700">
                    <span className="text-[10px] font-semibold text-sage-500 uppercase tracking-wider">Weave & Structure</span>
                    <p className="font-bold text-base text-forest-900 dark:text-cream-100 mt-1">{analysis.weave}</p>
                    <span className="text-xs text-sage-600 dark:text-sage-400 mt-1 block">Thickness: {analysis.thickness} | Drape: {analysis.drape}</span>
                  </div>

                  <div className="p-4 rounded-xl bg-sage-50 dark:bg-charcoal-900/50 border border-sage-200 dark:border-charcoal-700">
                    <span className="text-[10px] font-semibold text-sage-500 uppercase tracking-wider">Extracted Color Palette</span>
                    <div className="mt-2">
                      <ColorSwatch colors={[...(analysis.dominant_colors || []), ...(analysis.secondary_colors || [])]} size="md" />
                    </div>
                  </div>
                </div>
              )}
            </Card>
          )}
        </main>
      </div>
    </div>
  );
};
