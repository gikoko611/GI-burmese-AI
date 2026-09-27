import React from 'react';
import { ArrowRight, Video, FileText, Mic, Subtitles } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <section className="relative pt-6 pb-6 sm:pt-10 sm:pb-8 text-center max-w-4xl mx-auto px-4 sm:px-6">
      {/* Badge */}
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900/90 border border-zinc-800 text-xs font-medium text-amber-400 mb-4 tracking-wider uppercase">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
        G.I CONTENT AI
      </div>

      {/* Headline */}
      <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-zinc-100 tracking-tight leading-tight">
        Turn video content into <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-200 to-amber-500 font-burmese font-bold">Burmese</span>.
      </h1>

      {/* Description */}
      <p className="mt-3.5 sm:mt-4 text-base sm:text-lg text-zinc-400 max-w-2xl mx-auto leading-relaxed">
        Transform tutorials, stories, technology, tips and explanations into clear Burmese content.
      </p>

      {/* Pipeline Concept Flow */}
      <div className="mt-6 p-3 sm:p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/80 backdrop-blur-sm max-w-2xl mx-auto">
        <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3 text-xs sm:text-xs font-medium text-zinc-400">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-800/60 text-zinc-200">
            <Video className="w-3.5 h-3.5 text-red-400" />
            <span>YouTube URL</span>
          </div>

          <ArrowRight className="w-3.5 h-3.5 text-zinc-600 hidden sm:block" />

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-800/60 text-zinc-200">
            <span>Content Type</span>
          </div>

          <ArrowRight className="w-3.5 h-3.5 text-zinc-600 hidden sm:block" />

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-300">
            <FileText className="w-3.5 h-3.5 text-amber-400" />
            <span>Burmese Script</span>
          </div>

          <ArrowRight className="w-3.5 h-3.5 text-zinc-600 hidden sm:block" />

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900/60 text-zinc-500 border border-zinc-800/50">
            <Mic className="w-3.5 h-3.5 text-zinc-500" />
            <span>Voice (Future)</span>
          </div>

          <ArrowRight className="w-3.5 h-3.5 text-zinc-600 hidden sm:block" />

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900/60 text-zinc-500 border border-zinc-800/50">
            <Subtitles className="w-3.5 h-3.5 text-zinc-500" />
            <span>Captions (Future)</span>
          </div>
        </div>
      </div>
    </section>
  );
};
