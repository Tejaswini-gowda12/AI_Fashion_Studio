import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Send, Bot, User as UserIcon, Sparkles, Plus, Check } from 'lucide-react';
import { assistantService, projectService } from '../services/api';
import { ChatMessage, Project, DesignConcept } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const AssistantChatPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      if (!projectId) return;
      try {
        const proj = await projectService.get(parseInt(projectId));
        setProject(proj);
        const history = await assistantService.getChatHistory(parseInt(projectId));
        setMessages(history);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [projectId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const content = textToSend || input;
    if (!content.trim() || !projectId) return;

    setSending(true);
    setInput('');
    try {
      const res = await assistantService.sendMessage(parseInt(projectId), content);
      setMessages(prev => [...prev, res]);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const handleSaveConcept = async (conceptData: Partial<DesignConcept>) => {
    if (!projectId) return;
    try {
      await assistantService.createConcept({
        ...conceptData,
        project_id: parseInt(projectId)
      });
      alert('Design concept saved to project workspace!');
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

  const starterPrompts = [
    'Generate a 100% vegan redesign concept for this garment.',
    'Suggest low-water fabric alternatives retaining the same weave.',
    'Propose a low-cost eco production plan for medium budget.',
    'Explain botanical dyeing process for organic hemp.'
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row gap-8">
        <Sidebar
          projectId={project.id}
          projectTitle={project.title}
          hasAnalysis={true}
          hasFabricSelected={true}
        />

        <main className="flex-1 space-y-4 flex flex-col h-[750px]">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-forest-900 dark:text-cream-100">Step 5: AI Sustainable Fashion Assistant</h1>
              <p className="text-xs text-sage-600 dark:text-sage-400">Co-design eco concepts, refine material specs, and generate structured specs.</p>
            </div>
            <Button
              onClick={() => navigate(`/projects/${project.id}/concepts`)}
              variant="outline"
              size="sm"
            >
              View Saved Visual Renders
            </Button>
          </div>

          {/* Chat Messages Log */}
          <Card className="flex-1 overflow-y-auto p-4 space-y-4 bg-cream-50/50 dark:bg-charcoal-900/50 border-cream-200 dark:border-charcoal-700">
            {messages.length === 0 ? (
              <div className="text-center py-12 space-y-3">
                <Bot className="w-12 h-12 text-forest-700 mx-auto" />
                <h3 className="font-bold text-base text-forest-900 dark:text-cream-100">AI Fashion Co-Pilot Ready</h3>
                <p className="text-xs text-sage-600 dark:text-sage-400 max-w-md mx-auto">
                  Ask questions about fabric drape, vegan replacements, or click a starter prompt below.
                </p>
              </div>
            ) : (
              messages.map((msg) => {
                const isUser = msg.sender === 'user';
                const concept = msg.metadata_json?.structured_concept;
                return (
                  <div key={msg.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
                    {!isUser && (
                      <div className="w-8 h-8 rounded-full gradient-eco-badge text-cream-100 flex items-center justify-center shrink-0">
                        <Bot className="w-4 h-4" />
                      </div>
                    )}

                    <div className={`max-w-xl space-y-3 ${isUser ? 'items-end' : 'items-start'}`}>
                      <div
                        className={`p-4 rounded-2xl text-xs leading-relaxed ${
                          isUser
                            ? 'bg-forest-900 text-cream-100 font-medium'
                            : 'bg-white dark:bg-charcoal-800 text-charcoal-800 dark:text-cream-100 border border-cream-200 dark:border-charcoal-700 shadow-sm'
                        }`}
                      >
                        {msg.content}
                      </div>

                      {/* Structured Concept Card in Assistant Response */}
                      {concept && (
                        <div className="p-4 rounded-2xl bg-forest-50 dark:bg-forest-950/40 border border-forest-800/30 text-xs space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-forest-900 dark:text-cream-100">{concept.design_name}</span>
                            <Button size="sm" onClick={() => handleSaveConcept(concept)} className="gap-1 text-[11px] py-1 px-2">
                              <Plus className="w-3 h-3" /> Save Concept Card
                            </Button>
                          </div>
                          <p className="text-sage-700 dark:text-sage-300">{concept.inspiration_summary}</p>
                          <div className="text-[11px] text-sage-600 space-y-0.5">
                            <div><strong className="text-forest-900 dark:text-sage-300">Material:</strong> {concept.material_recommendation}</div>
                            <div><strong className="text-forest-900 dark:text-sage-300">Dyeing:</strong> {concept.dyeing_method}</div>
                            <div><strong className="text-forest-900 dark:text-sage-300">Rationale:</strong> {concept.sustainability_rationale}</div>
                          </div>
                        </div>
                      )}
                    </div>

                    {isUser && (
                      <div className="w-8 h-8 rounded-full bg-sage-300 dark:bg-charcoal-700 text-forest-900 dark:text-cream-100 flex items-center justify-center font-bold text-xs shrink-0">
                        <UserIcon className="w-4 h-4" />
                      </div>
                    )}
                  </div>
                );
              })
            )}
            <div ref={chatEndRef} />
          </Card>

          {/* Starter Quick Prompts */}
          <div className="flex flex-wrap gap-2">
            {starterPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt)}
                className="text-[11px] font-medium px-3 py-1.5 rounded-full bg-sage-100 dark:bg-charcoal-800 text-forest-900 dark:text-sage-300 hover:bg-forest-900 hover:text-white transition-colors border border-sage-300 dark:border-charcoal-700"
              >
                + {prompt}
              </button>
            ))}
          </div>

          {/* Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask AI Assistant to refine material, silhouette, or low-cost dyeing..."
              className="flex-1 px-4 py-3 rounded-2xl border border-cream-300 dark:border-charcoal-700 bg-white dark:bg-charcoal-800 text-xs focus:outline-none focus:ring-2 focus:ring-forest-900"
            />
            <Button type="submit" disabled={sending || !input.trim()} className="py-3 px-5 rounded-2xl">
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </main>
      </div>
    </div>
  );
};
