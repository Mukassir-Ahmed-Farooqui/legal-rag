import React, { useState } from 'react';
import { Shield, Search, Bookmark, Files, ShieldCheck, MessageSquare } from 'lucide-react';
import { AuthModal } from '../auth/AuthModal';

export const LandingPage = () => {
  const [authMode, setAuthMode] = useState(null); // 'login' | 'register' | null

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-md border-b border-slate-100 z-40">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded bg-primary flex items-center justify-center text-white">
              <Shield className="h-5 w-5" />
            </div>
            <span className="font-bold text-lg tracking-tight">OpenDoc</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#how-it-works" className="hover:text-primary transition-colors">How it works</a>
            <a href="#features" className="hover:text-primary transition-colors">Features</a>
          </div>
          <div className="flex items-center gap-4">
            <a 
              href="https://github.com/Mukassir-Ahmed-Farooqui/legal-rag" 
              target="_blank" 
              rel="noreferrer"
              className="hidden md:flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              <svg viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.24c3-.3 6-1.5 6-6.76 0-1.5-.5-2.8-1.4-3.8.1-.3.6-1.8-.1-3.8 0 0-1.2-.4-3.9 1.4a12.3 12.3 0 0 0-7 0C3.7 3.6 2.5 4 2.5 4c-.7 2-.2 3.5-.1 3.8A6.7 6.7 0 0 0 1 11.6c0 5.2 3 6.4 6 6.76-.7.6-1 1.5-1 3.24v4"></path>
                <path d="M9 19c-4 1-5-2-7-2"></path>
              </svg>
              Open source
            </a>
            <button 
              onClick={() => setAuthMode('login')}
              className="text-sm font-semibold text-slate-700 hover:text-primary transition-colors px-2"
            >
              Sign in
            </button>
            <button 
              onClick={() => setAuthMode('register')}
              className="text-sm font-semibold bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all shadow-sm"
            >
              Get started free
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <main className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-600">
            <span>✦</span> Hybrid retrieval · Evidence-backed answers · Open source
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 leading-[1.1]">
            Ask anything about <br/>
            <span className="text-primary">your documents</span>
          </h1>
          <p className="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Upload any PDF. Ask questions in plain language. Get precise, cited answers backed by evidence — not guesses. Works on contracts, research papers, reports, policies, and more.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button 
              onClick={() => setAuthMode('register')}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-primary text-white font-semibold shadow-lg shadow-blue-500/25 hover:bg-blue-700 hover:shadow-blue-500/40 hover:-translate-y-0.5 transition-all"
            >
              Get started free
            </button>
            <a 
              href="#how-it-works"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-white border border-slate-200 text-slate-700 font-semibold hover:bg-slate-50 transition-all"
            >
              See how it works
            </a>
          </div>
          <p className="text-xs text-slate-400 font-medium pt-2">
            No credit card required · Open source · Your documents stay private
          </p>
        </div>

        {/* UI Mockup */}
        <div className="max-w-5xl mx-auto mt-20">
          <div className="rounded-2xl border border-slate-200 bg-white shadow-2xl overflow-hidden">
            {/* Browser Header */}
            <div className="h-10 border-b border-slate-100 bg-slate-50 flex items-center px-4 gap-4">
              <div className="flex items-center gap-1.5">
                <div className="h-3 w-3 rounded-full bg-red-400"></div>
                <div className="h-3 w-3 rounded-full bg-amber-400"></div>
                <div className="h-3 w-3 rounded-full bg-green-400"></div>
              </div>
              <div className="flex-1 max-w-sm mx-auto h-6 bg-white rounded-md border border-slate-200 flex items-center justify-center text-[10px] font-medium text-slate-400">
                app.opendoc.ai
              </div>
            </div>
            {/* Mockup Body */}
            <div className="h-[400px] flex">
              {/* Sidebar */}
              <div className="w-48 border-r border-slate-100 bg-slate-50 p-4 space-y-3">
                <div className="h-4 w-20 bg-slate-200 rounded"></div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2"><div className="h-3 w-3 border border-slate-300 rounded"></div><div className="h-3 w-24 bg-slate-200 rounded"></div></div>
                  <div className="flex items-center gap-2"><div className="h-3 w-3 bg-primary rounded"></div><div className="h-3 w-20 bg-slate-200 rounded"></div></div>
                  <div className="flex items-center gap-2"><div className="h-3 w-3 bg-primary rounded"></div><div className="h-3 w-28 bg-slate-200 rounded"></div></div>
                </div>
              </div>
              {/* Chat Area */}
              <div className="flex-1 p-6 flex flex-col justify-between">
                <div className="space-y-6">
                  {/* User msg */}
                  <div className="flex justify-end">
                    <div className="bg-slate-100 rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%]">
                      <div className="h-3 w-48 bg-slate-400 rounded"></div>
                    </div>
                  </div>
                  {/* AI msg */}
                  <div className="flex justify-start">
                    <div className="bg-blue-50/50 border border-blue-100 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[80%] space-y-3">
                      <div className="h-3 w-full bg-slate-600 rounded"></div>
                      <div className="h-3 w-3/4 bg-slate-600 rounded"></div>
                      <div className="flex gap-2 pt-2">
                        <div className="h-5 w-8 bg-blue-100 rounded flex items-center justify-center text-[9px] font-bold text-blue-600">[1]</div>
                        <div className="h-5 w-8 bg-blue-100 rounded flex items-center justify-center text-[9px] font-bold text-blue-600">[2]</div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Input */}
                <div className="h-12 border border-slate-200 rounded-xl bg-slate-50 flex items-center px-4">
                  <div className="h-4 w-32 bg-slate-200 rounded"></div>
                </div>
              </div>
              {/* Context Cards */}
              <div className="w-64 border-l border-slate-100 bg-white p-4 space-y-4">
                <div className="h-4 w-24 bg-slate-200 rounded mb-4"></div>
                <div className="p-3 border border-slate-100 rounded-lg shadow-sm space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="h-2 w-16 bg-blue-200 rounded"></div>
                    <div className="h-3 w-8 bg-slate-200 rounded"></div>
                  </div>
                  <div className="h-2 w-full bg-slate-100 rounded"></div>
                  <div className="h-2 w-full bg-slate-100 rounded"></div>
                  <div className="h-2 w-2/3 bg-slate-100 rounded"></div>
                </div>
                <div className="p-3 border border-slate-100 rounded-lg shadow-sm space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="h-2 w-20 bg-blue-200 rounded"></div>
                    <div className="h-3 w-8 bg-slate-200 rounded"></div>
                  </div>
                  <div className="h-2 w-full bg-slate-100 rounded"></div>
                  <div className="h-2 w-3/4 bg-slate-100 rounded"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* How it works */}
      <section id="how-it-works" className="py-24 bg-slate-50 border-t border-b border-slate-100">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-extrabold text-center mb-16">How it works</h2>
          <div className="grid md:grid-cols-3 gap-12 text-center md:text-left">
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-full bg-blue-100 text-primary flex items-center justify-center font-bold text-xl mx-auto md:mx-0">①</div>
              <h3 className="text-xl font-bold">Upload</h3>
              <p className="text-slate-600 leading-relaxed">Upload your PDFs. Documents are indexed for intelligent retrieval.</p>
            </div>
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-full bg-blue-100 text-primary flex items-center justify-center font-bold text-xl mx-auto md:mx-0">②</div>
              <h3 className="text-xl font-bold">Ask</h3>
              <p className="text-slate-600 leading-relaxed">Ask anything in plain language. No special syntax needed.</p>
            </div>
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-full bg-blue-100 text-primary flex items-center justify-center font-bold text-xl mx-auto md:mx-0">③</div>
              <h3 className="text-xl font-bold">Get cited answers</h3>
              <p className="text-slate-600 leading-relaxed">Receive precise answers with exact page and section citations. Evidence, not guesses.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-extrabold text-center mb-16">Features</h2>
          <div className="grid md:grid-cols-3 gap-x-8 gap-y-12">
            <FeatureCard 
              icon={<Search />} 
              title="Hybrid Retrieval" 
              desc="Dense + BM25 + RRF fusion finds the exact clause — even when you don't use the right keywords."
            />
            <FeatureCard 
              icon={<Bookmark />} 
              title="Evidence-backed answers" 
              desc="Every answer cites the exact page and section it came from. No hallucinations, no guessing."
            />
            <FeatureCard 
              icon={<Files />} 
              title="Document workspace" 
              desc="Select which documents to query. Chat history is saved. Your workspace picks up where you left off."
            />
            <FeatureCard 
              icon={<ShieldCheck />} 
              title="Your documents stay yours" 
              desc="Full ownership enforcement. No one else can ever access your documents."
            />
            <FeatureCard 
              icon={<MessageSquare />} 
              title="Chat history" 
              desc="Every conversation is saved. Pick up any thread from any previous session."
            />
            <FeatureCard 
              icon={<svg viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.24c3-.3 6-1.5 6-6.76 0-1.5-.5-2.8-1.4-3.8.1-.3.6-1.8-.1-3.8 0 0-1.2-.4-3.9 1.4a12.3 12.3 0 0 0-7 0C3.7 3.6 2.5 4 2.5 4c-.7 2-.2 3.5-.1 3.8A6.7 6.7 0 0 0 1 11.6c0 5.2 3 6.4 6 6.76-.7.6-1 1.5-1 3.24v4"></path><path d="M9 19c-4 1-5-2-7-2"></path></svg>} 
              title="Open source" 
              desc="Fully open source. Self-host it, audit it, extend it. Built in public from day one."
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-slate-900 text-white text-center">
        <div className="max-w-3xl mx-auto px-6 space-y-8">
          <h2 className="text-4xl font-extrabold">Ready to understand your documents?</h2>
          <p className="text-xl text-slate-400">Upload your first document in under a minute.</p>
          <button 
            onClick={() => setAuthMode('register')}
            className="px-8 py-4 rounded-xl bg-primary text-white font-bold text-lg hover:bg-blue-600 transition-colors shadow-lg"
          >
            Get started free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-slate-500 font-medium">
          <div>© 2025 OpenDoc. Open source.</div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-slate-900">Privacy</a>
            <a href="https://github.com/Mukassir-Ahmed-Farooqui/legal-rag" target="_blank" rel="noreferrer" className="hover:text-slate-900">GitHub</a>
          </div>
        </div>
      </footer>

      {authMode && (
        <AuthModal 
          mode={authMode} 
          onClose={() => setAuthMode(null)} 
          onSwitchMode={setAuthMode} 
        />
      )}
    </div>
  );
};

const FeatureCard = ({ icon, title, desc }) => (
  <div className="space-y-4">
    <div className="h-10 w-10 rounded-lg bg-blue-50 text-primary flex items-center justify-center">
      {React.cloneElement(icon, { className: 'h-5 w-5' })}
    </div>
    <h3 className="text-lg font-bold text-slate-900">{title}</h3>
    <p className="text-sm text-slate-600 leading-relaxed">{desc}</p>
  </div>
);
