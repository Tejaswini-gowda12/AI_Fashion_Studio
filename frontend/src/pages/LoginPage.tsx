import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, Lock, Mail, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid login credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = async (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setLoading(true);
    try {
      await login(demoEmail, demoPass);
      navigate('/dashboard');
    } catch (err: any) {
      setError('Demo login failed. Make sure backend seed database is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-cream-100 dark:bg-charcoal-900">
      <div className="max-w-md w-full bg-white dark:bg-charcoal-800 rounded-3xl p-8 shadow-xl border border-cream-200 dark:border-charcoal-700">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-2xl gradient-eco-badge flex items-center justify-center mx-auto mb-3 shadow-md">
            <Leaf className="w-6 h-6 text-cream-100" />
          </div>
          <h2 className="text-2xl font-bold text-forest-900 dark:text-cream-100">Welcome Back</h2>
          <p className="text-xs text-sage-600 dark:text-sage-400 mt-1">Sign in to access your sustainable fashion workspace</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs font-semibold">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-sage-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="designer@eco.fashion"
                className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-sm focus:outline-none focus:ring-2 focus:ring-forest-900 dark:focus:ring-sage-400"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-sage-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-sm focus:outline-none focus:ring-2 focus:ring-forest-900 dark:focus:ring-sage-400"
              />
            </div>
          </div>

          <Button type="submit" disabled={loading} className="w-full py-3 mt-2 font-semibold">
            {loading ? 'Authenticating...' : 'Sign In'}
          </Button>
        </form>

        <div className="mt-6 pt-6 border-t border-cream-200 dark:border-charcoal-700">
          <p className="text-xs text-center text-sage-600 dark:text-sage-400 mb-3 font-semibold">Quick Demo Login</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleQuickDemo('designer@eco.fashion', 'designer123')}
              className="py-2 px-3 rounded-xl border border-forest-800/30 text-forest-900 dark:text-sage-300 bg-forest-50/50 dark:bg-forest-950/40 text-xs font-semibold hover:bg-forest-100 transition-colors flex items-center justify-center gap-1"
            >
              <Leaf className="w-3.5 h-3.5 text-forest-700" /> Designer Demo
            </button>
            <button
              onClick={() => handleQuickDemo('admin@eco.fashion', 'admin123')}
              className="py-2 px-3 rounded-xl border border-terracotta-500/30 text-terracotta-700 dark:text-terracotta-300 bg-terracotta-50/50 dark:bg-terracotta-950/40 text-xs font-semibold hover:bg-terracotta-100 transition-colors flex items-center justify-center gap-1"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-terracotta-500" /> Admin Demo
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-sage-600 dark:text-sage-400 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="font-bold text-forest-900 dark:text-sage-300 hover:underline">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
};
