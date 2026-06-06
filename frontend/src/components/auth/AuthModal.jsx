import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../../hooks/useAuth';

export const AuthModal = ({ mode, onClose, onSwitchMode }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const isLogin = mode === 'login';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password, fullName);
      }
      onClose();
      navigate('/chat');
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail || 'Invalid email or password';
      setError(detail);
      // Not using toast for auth errors per requirements
    } finally {
      setLoading(false);
    }
  };

  const handleSocialClick = (provider) => {
    toast(`${provider} login coming soon`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="p-8">
          <div className="flex flex-col items-center justify-center text-center mb-8">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-primary mb-4">
              <Shield className="h-6 w-6" />
            </div>
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              {isLogin ? 'Welcome back' : 'Create your account'}
            </h2>
            <p className="text-sm text-slate-500 mt-1 font-medium">
              {isLogin ? 'Sign in to your workspace' : 'Start analyzing your documents'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-sm font-medium text-red-600 bg-red-50 border border-red-100 rounded-lg text-center">
                {error}
              </div>
            )}

            {!isLogin && (
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-sm outline-none"
                  placeholder="Jane Doe"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-sm outline-none"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-sm outline-none"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 bg-primary text-white font-bold text-sm rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-primary/20 transition-all disabled:opacity-50 mt-2"
            >
              {loading ? (isLogin ? 'Signing in...' : 'Creating account...') : (isLogin ? 'Sign in' : 'Create account')}
            </button>
          </form>

          <div className="my-6 flex items-center">
            <div className="flex-1 border-t border-slate-100"></div>
            <span className="px-4 text-xs font-semibold text-slate-400 uppercase">or</span>
            <div className="flex-1 border-t border-slate-100"></div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleSocialClick('GitHub')}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <svg viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.24c3-.3 6-1.5 6-6.76 0-1.5-.5-2.8-1.4-3.8.1-.3.6-1.8-.1-3.8 0 0-1.2-.4-3.9 1.4a12.3 12.3 0 0 0-7 0C3.7 3.6 2.5 4 2.5 4c-.7 2-.2 3.5-.1 3.8A6.7 6.7 0 0 0 1 11.6c0 5.2 3 6.4 6 6.76-.7.6-1 1.5-1 3.24v4"></path>
                <path d="M9 19c-4 1-5-2-7-2"></path>
              </svg>
              GitHub
            </button>
            <button
              type="button"
              onClick={() => handleSocialClick('Google')}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google
            </button>
          </div>

          <div className="mt-8 text-center">
            <button
              onClick={() => onSwitchMode(isLogin ? 'register' : 'login')}
              className="text-sm font-semibold text-slate-500 hover:text-slate-900 transition-colors"
            >
              {isLogin ? "Don't have an account? Create one" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
