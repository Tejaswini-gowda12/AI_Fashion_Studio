import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Image as ImageIcon, Sparkles, Layers, Maximize2, RefreshCw } from 'lucide-react';
import { assistantService, projectService } from '../services/api';
import { GeneratedImage, DesignConcept, Project } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { ColorSwatch } from '../components/ui/ColorSwatch';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const GeneratedConceptsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [concepts, setConcepts] = useState<DesignConcept[]>([]);
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const [selectedConceptId, setSelectedConceptId] = useState<number | undefined>(undefined);
  const [promptSuffix, setPromptSuffix] = useState('');
  const [compareModalImage, setCompareModalImage] = useState<GeneratedImage | null>(null);

  useEffect(() => {
    const loadData = async () => {
      if (!projectId) return;
      try {
        const proj = await projectService.get(parseInt(projectId));
        setProject(proj);
        const cList = await assistantService.getConcepts(parseInt(projectId));
        setConcepts(cList);
        const imgList = await assistantService.getGeneratedImages(parseInt(projectId));
        setGeneratedImages(imgList);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [projectId]);

  const handleGenerate = async () => {
    if (!projectId) return;
    setGenerating(true);
    try {
      const newImg = await assistantService.generateConceptImage(
        parseInt(projectId),
        selectedConceptId,
        promptSuffix
      );
      setGeneratedImages(prev => [newImg, ...prev]);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  if (loading || !project) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <LoadingSkeleton />
      </div>
    );
  }

  const refImage = project.reference_images && project.reference_images.length > 0
    ? project.reference_images[project.reference_images.length - 1]
    : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row gap-8">
        <Sidebar
          projectId={project.id}
          projectTitle={project.title}
          hasAnalysis={true}
          hasFabricSelected={true}
        />

        <main className="flex-1 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-forest-900 dark:text-cream-100">Step 6: AI Concept Visualization & Comparator</h1>
              <p className="text-xs text-sage-600 dark:text-sage-400">Generate high-fidelity eco-concept fashion renders and compare side-by-side.</p>
            </div>
          </div>

          {/* Generator Controls */}
          <Card className="p-6 space-y-4">
            <h3 className="font-bold text-sm text-forest-900 dark:text-cream-100 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-terracotta-500" /> AI Concept Prompt Generator
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Target Design Concept</label>
                <select
                  value={selectedConceptId || ''}
                  onChange={(e) => setSelectedConceptId(e.target.value ? parseInt(e.target.value) : undefined)}
                  className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-xs"
                >
                  <option value="">-- Use Default Project Spec --</option>
                  {concepts.map((c) => (
                    <option key={c.id} value={c.id}>{c.design_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Custom Design Details / Lighting</label>
                <input
                  type="text"
                  value={promptSuffix}
                  onChange={(e) => setPromptSuffix(e.target.value)}
                  placeholder="e.g., Studio soft box lighting, relaxed drape, organic texture..."
                  className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-xs"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <Button onClick={handleGenerate} disabled={generating} className="gap-2 text-xs">
                {generating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                {generating ? 'Rendering AI Concept...' : 'Render Design Concept'}
              </Button>
            </div>
          </Card>

          {/* Generated Gallery */}
          <div className="space-y-4">
            <h3 className="font-bold text-base text-forest-900 dark:text-cream-100">Generated Eco Concept Cards</h3>

            {generatedImages.length === 0 ? (
              <Card className="text-center py-12">
                <ImageIcon className="w-10 h-10 text-sage-400 mx-auto mb-2" />
                <p className="text-sm font-semibold text-forest-900 dark:text-cream-100">No concept renders generated yet</p>
                <p className="text-xs text-sage-500 mt-1">Click "Render Design Concept" above to visualize sustainable designs.</p>
              </Card>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {generatedImages.map((img) => (
                  <Card key={img.id} className="p-4 space-y-3">
                    <div className="relative rounded-xl overflow-hidden bg-charcoal-950 aspect-[4/5] flex items-center justify-center">
                      <img src={img.image_url} alt="Concept Render" className="w-full h-full object-contain" />
                      <button
                        onClick={() => setCompareModalImage(img)}
                        className="absolute bottom-3 right-3 p-2 rounded-xl bg-black/70 text-white hover:bg-black transition-colors"
                        title="Side-by-side Comparator"
                      >
                        <Maximize2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="space-y-1">
                      <Badge variant="sage">{img.generation_mode.toUpperCase()} RENDER</Badge>
                      <p className="text-[11px] text-sage-600 dark:text-sage-400 line-clamp-2">{img.prompt}</p>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Side-by-Side Comparison Modal */}
          <Modal
            isOpen={!!compareModalImage}
            onClose={() => setCompareModalImage(null)}
            title="Side-by-Side Design Intent Comparator"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <span className="text-xs font-bold text-sage-600 block">Original Reference Inspiration</span>
                <div className="rounded-xl overflow-hidden bg-charcoal-950 aspect-[4/5] flex items-center justify-center border">
                  {refImage ? (
                    <img src={refImage.file_path} alt="Original Ref" className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-xs text-sage-400">No original reference image</span>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-bold text-forest-800 dark:text-sage-300 block">AI Sustainable Concept Render</span>
                <div className="rounded-xl overflow-hidden bg-charcoal-950 aspect-[4/5] flex items-center justify-center border border-forest-800">
                  {compareModalImage && (
                    <img src={compareModalImage.image_url} alt="Generated Concept" className="w-full h-full object-contain" />
                  )}
                </div>
              </div>
            </div>
          </Modal>
        </main>
      </div>
    </div>
  );
};
