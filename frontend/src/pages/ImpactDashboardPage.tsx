import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { Leaf, Droplets, Download, Info, CheckCircle2, TrendingDown, ArrowRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { impactService, projectService, analysisService } from '../services/api';
import { ImpactAssessment, Project, FabricAnalysis } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const ImpactDashboardPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const fabricIdParam = parseInt(searchParams.get('fabricId') || '1');
  const dyeIdParam = parseInt(searchParams.get('dyeId') || '1');

  const [project, setProject] = useState<Project | null>(null);
  const [analysis, setAnalysis] = useState<FabricAnalysis | null>(null);
  const [impact, setImpact] = useState<ImpactAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

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

          const impactRes = await impactService.calculate({
            analysis_id: lastAnalysis.id,
            selected_fabric_id: fabricIdParam,
            selected_dye_id: dyeIdParam
          });
          setImpact(impactRes);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [projectId, fabricIdParam, dyeIdParam]);

  const handleDownloadPdf = async () => {
    if (!analysis) return;
    setDownloading(true);
    try {
      const blob = await impactService.downloadPdfReport(analysis.id, fabricIdParam, dyeIdParam);
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sustainability_report_project_${projectId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
      alert('Failed to download PDF audit report.');
    } finally {
      setDownloading(false);
    }
  };

  if (loading || !project || !impact) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <LoadingSkeleton />
      </div>
    );
  }

  const chartData = [
    {
      name: 'Water Use (Liters)',
      Conventional: impact.water_comparison.conventional,
      Sustainable: impact.water_comparison.sustainable
    },
    {
      name: 'CO2 Emissions (kg)',
      Conventional: impact.co2_comparison.conventional,
      Sustainable: impact.co2_comparison.sustainable
    }
  ];

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
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-forest-900 dark:text-cream-100">Step 4: Environmental Impact Assessment</h1>
              <p className="text-xs text-sage-600 dark:text-sage-400">Comparing baseline conventional materials against your chosen sustainable choices.</p>
            </div>

            <div className="flex items-center space-x-2">
              <Button
                variant="secondary"
                onClick={handleDownloadPdf}
                disabled={downloading}
                className="gap-2 text-xs py-2"
              >
                <Download className="w-4 h-4" />
                {downloading ? 'Generating PDF...' : 'Download Audit PDF Report'}
              </Button>
            </div>
          </div>

          {/* Key Lifecycle Benefit Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-blue-50 to-white dark:from-charcoal-800 dark:to-charcoal-900 border-blue-200">
              <div className="flex items-center space-x-3 mb-2">
                <div className="p-2 rounded-xl bg-blue-500/10 text-blue-600">
                  <Droplets className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-sage-600 dark:text-sage-400">Water Conserved</span>
              </div>
              <p className="text-2xl font-extrabold text-blue-700 dark:text-blue-400">{impact.water_saved_liters} L</p>
              <p className="text-[11px] text-sage-500 mt-1">Per individual garment produced</p>
            </Card>

            <Card className="bg-gradient-to-br from-terracotta-50 to-white dark:from-charcoal-800 dark:to-charcoal-900 border-terracotta-200">
              <div className="flex items-center space-x-3 mb-2">
                <div className="p-2 rounded-xl bg-terracotta-500/10 text-terracotta-500">
                  <TrendingDown className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-sage-600 dark:text-sage-400">CO2 Emissions Avoided</span>
              </div>
              <p className="text-2xl font-extrabold text-terracotta-600 dark:text-terracotta-400">{impact.co2_reduced_kg} kg</p>
              <p className="text-[11px] text-sage-500 mt-1">LCA greenhouse gas reduction</p>
            </Card>

            <Card className="bg-gradient-to-br from-forest-50 to-white dark:from-charcoal-800 dark:to-charcoal-900 border-forest-200">
              <div className="flex items-center space-x-3 mb-2">
                <div className="p-2 rounded-xl bg-forest-900/10 text-forest-800 dark:text-sage-300">
                  <Leaf className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-sage-600 dark:text-sage-400">Chemical Toxicity</span>
              </div>
              <p className="text-2xl font-extrabold text-forest-800 dark:text-sage-300">-{impact.chemical_reduction_pct}%</p>
              <p className="text-[11px] text-sage-500 mt-1">Non-toxic botanical/low-impact dye</p>
            </Card>

            <Card className="bg-gradient-to-br from-amber-50 to-white dark:from-charcoal-800 dark:to-charcoal-900 border-amber-200">
              <div className="flex items-center space-x-3 mb-2">
                <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-sage-600 dark:text-sage-400">Waste Diverted</span>
              </div>
              <p className="text-2xl font-extrabold text-amber-700 dark:text-amber-400">{impact.waste_reduced_kg} kg</p>
              <p className="text-[11px] text-sage-500 mt-1">Zero landfill textile scrap goal</p>
            </Card>
          </div>

          {/* Recharts Environmental Comparison Graph */}
          <Card className="p-6">
            <h3 className="font-bold text-base text-forest-900 dark:text-cream-100 mb-4">Lifecycle Savings Comparison (Baseline vs Sustainable)</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" stroke="#8A9A86" fontSize={12} />
                  <YAxis stroke="#8A9A86" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1C3A27',
                      borderColor: '#8A9A86',
                      borderRadius: '12px',
                      color: '#F9F7F1',
                      fontSize: '12px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="Conventional" fill="#C86D51" radius={[6, 6, 0, 0]} name="Conventional Cotton Baseline" />
                  <Bar dataKey="Sustainable" fill="#1C3A27" radius={[6, 6, 0, 0]} name="Selected Sustainable Alternative" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Executive Summary & Modeling Assumptions */}
          <Card className="space-y-4">
            <div className="p-4 rounded-xl bg-forest-900 text-cream-100">
              <span className="text-[10px] font-bold text-sage-300 uppercase tracking-wider block mb-1">AUDIT SUMMARY STATEMENT</span>
              <p className="text-sm font-semibold leading-relaxed">{impact.summary_text}</p>
            </div>

            <div className="p-4 rounded-xl bg-sage-50 dark:bg-charcoal-900 border border-sage-200 dark:border-charcoal-700">
              <h4 className="font-bold text-xs text-forest-900 dark:text-cream-100 flex items-center gap-1.5 mb-2">
                <Info className="w-4 h-4 text-forest-700" /> Lifecycle Modeling Disclosures & Transparency
              </h4>
              <ul className="space-y-1.5 text-xs text-sage-600 dark:text-sage-400">
                {impact.assumptions.map((note, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-forest-700">•</span>
                    <span>{note}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>

          {/* Next Steps: AI Assistant & Concept Viz */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-cream-200 dark:border-charcoal-700">
            <Link to={`/projects/${project.id}/chat`}>
              <Button variant="outline" size="sm" className="gap-2">
                Refine Design with AI Assistant
              </Button>
            </Link>
            <Link to={`/projects/${project.id}/concepts`}>
              <Button variant="primary" size="sm" className="gap-2">
                Generate Visual Concept Renders <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </main>
      </div>
    </div>
  );
};
