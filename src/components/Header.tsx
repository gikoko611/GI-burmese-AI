import React from 'react';
import { Sparkles, Terminal } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-40 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Brand & Identity */}
        <div className="flex items-center gap-3.5">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center font-bold text-zinc-950 text-base tracking-wider shadow-sm ring-1 ring-amber-400/30">
            G.I
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-zinc-100 text-base tracking-tight">
                G.I Burmese AI
              </span>
              <span className="hidden sm:inline-block text-xs text-zinc-500">v0.9-alpha</span>
            </div>
            <span className="text-xs text-zinc-400 tracking-wide font-normal">
              AI-powered Burmese content
            </span>
          </div>
        </div>

        {/* Right: Cloud Ready Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-300">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="tracking-wide">Cloud Ready</span>
          </div>
          
          <div className="hidden md:flex items-center gap-1.5 text-xs text-zinc-500 pl-2 border-l border-zinc-800">
            <Terminal className="w-3.5 h-3.5 text-zinc-400" />
            <span>FastAPI Spec</span>
          </div>
        </div>
      </div>
    </header>
  );
};
