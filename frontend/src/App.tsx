import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { ProtectedRoute } from './components/layout/ProtectedRoute';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { FabricDetectionPage } from './pages/FabricDetectionPage';
import { DashboardPage } from './pages/DashboardPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { ProjectDetailPage } from './pages/ProjectDetailPage';
import { AnalysisWorkspacePage } from './pages/AnalysisWorkspacePage';
import { FabricRecommendationsPage } from './pages/FabricRecommendationsPage';
import { DyeRecommendationsPage } from './pages/DyeRecommendationsPage';
import { ImpactDashboardPage } from './pages/ImpactDashboardPage';
import { AssistantChatPage } from './pages/AssistantChatPage';
import { GeneratedConceptsPage } from './pages/GeneratedConceptsPage';
import { ProfilePage } from './pages/ProfilePage';
import { AdminCatalogPage } from './pages/AdminCatalogPage';
import { OutfitStudioPage } from './pages/OutfitStudioPage';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen flex flex-col bg-cream-100 dark:bg-charcoal-900 text-charcoal-800 dark:text-cream-100 transition-colors">
            <Navbar />
            <div className="flex-1">
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/fabric-detection" element={<FabricDetectionPage />} />
                <Route path="/outfit-studio" element={<OutfitStudioPage />} />

                {/* Protected Designer Routes */}
                <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
                <Route path="/projects" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
                <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
                <Route path="/projects/:projectId/analysis" element={<ProtectedRoute><AnalysisWorkspacePage /></ProtectedRoute>} />
                <Route path="/projects/:projectId/recommendations" element={<ProtectedRoute><FabricRecommendationsPage /></ProtectedRoute>} />
                <Route path="/projects/:projectId/dyeing" element={<ProtectedRoute><DyeRecommendationsPage /></ProtectedRoute>} />
                <Route path="/projects/:projectId/impact" element={<ProtectedRoute><ImpactDashboardPage /></ProtectedRoute>} />
                <Route path="/projects/:projectId/chat" element={<ProtectedRoute><AssistantChatPage /></ProtectedRoute>} />
                <Route path="/projects/:projectId/concepts" element={<ProtectedRoute><GeneratedConceptsPage /></ProtectedRoute>} />
                <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

                {/* Admin Only Route */}
                <Route path="/admin" element={<ProtectedRoute adminOnly><AdminCatalogPage /></ProtectedRoute>} />

                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
            <Footer />
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};
