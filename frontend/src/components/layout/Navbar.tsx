import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, Sun, Moon, LogOut, User as UserIcon, LayoutDashboard, FolderKanban, ShieldCheck, Sparkles, Wand2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="navbar glass-panel border-b border-cream-200 dark:border-charcoal-800 transition-colors shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl gradient-eco-badge flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
            <Leaf className="w-5 h-5 text-cream-100" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight text-forest-900 dark:text-cream-100 flex items-center gap-1.5">
              EcoFabric <span className="text-xs px-2 py-0.5 rounded-full bg-sage-100 dark:bg-forest-900 text-forest-700 dark:text-sage-300 font-semibold border border-sage-300 dark:border-forest-700">AI Fashion</span>
            </span>
            <p className="text-[10px] text-sage-600 dark:text-sage-400 font-medium">Sustainable Design Assistant</p>
          </div>
        </Link>

        <nav className="hidden md:flex items-center space-x-1 font-medium text-sm">
          <Link to="/fabric-detection" className="px-3.5 py-2 rounded-lg text-forest-800 dark:text-sage-300 bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900 transition-colors flex items-center gap-2 font-semibold border border-emerald-200 dark:border-emerald-800">
            <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Fabric Detection
          </Link>
          <Link to="/outfit-studio" className="px-3.5 py-2 rounded-lg text-violet-900 dark:text-violet-300 bg-violet-50 dark:bg-violet-950/60 hover:bg-violet-100 dark:hover:bg-violet-900 transition-colors flex items-center gap-2 font-semibold border border-violet-200 dark:border-violet-800">
            <Wand2 className="w-4 h-4 text-violet-600 dark:text-violet-400" />
            AI Outfit Studio
          </Link>
          {user && (
            <>
              <Link to="/dashboard" className="px-3.5 py-2 rounded-lg text-charcoal-800 dark:text-cream-200 hover:bg-sage-100 dark:hover:bg-charcoal-800 transition-colors flex items-center gap-2">
                <LayoutDashboard className="w-4 h-4 text-forest-600 dark:text-sage-400" />
                Dashboard
              </Link>
              <Link to="/projects" className="px-3.5 py-2 rounded-lg text-charcoal-800 dark:text-cream-200 hover:bg-sage-100 dark:hover:bg-charcoal-800 transition-colors flex items-center gap-2">
                <FolderKanban className="w-4 h-4 text-terracotta-500" />
                Projects
              </Link>
              {user.role === 'admin' && (
                <Link to="/admin" className="px-3.5 py-2 rounded-lg text-forest-800 dark:text-sage-300 bg-sage-50 dark:bg-forest-950 hover:bg-sage-100 dark:hover:bg-forest-900 transition-colors flex items-center gap-2 border border-sage-200 dark:border-forest-800 font-semibold">
                  <ShieldCheck className="w-4 h-4 text-forest-600" />
                  Admin Catalog
                </Link>
              )}
            </>
          )}
        </nav>

        <div className="flex items-center space-x-3">
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-xl text-charcoal-800 dark:text-cream-100 hover:bg-cream-200 dark:hover:bg-charcoal-800 transition-colors"
            title="Toggle theme"
          >
            {darkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-forest-900" />}
          </button>

          {user ? (
            <div className="flex items-center space-x-2">
              <Link
                to="/profile"
                className="flex items-center space-x-2 px-3 py-1.5 rounded-xl hover:bg-sage-100 dark:hover:bg-charcoal-800 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-forest-900 text-cream-100 flex items-center justify-center font-bold text-xs">
                  {user.full_name.charAt(0).toUpperCase()}
                </div>
                <span className="hidden sm:inline font-medium text-xs text-charcoal-800 dark:text-cream-100">{user.full_name}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="p-2 rounded-xl text-stone-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Link to="/login" className="px-4 py-2 text-sm font-semibold text-forest-900 dark:text-cream-100 hover:text-forest-700 transition-colors">
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 text-sm font-semibold rounded-xl bg-forest-900 text-cream-100 hover:bg-forest-800 shadow-sm transition-all"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
