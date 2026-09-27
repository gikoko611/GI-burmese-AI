import React from 'react';
import { Subtitles, Lock, FileCode, Download, Sparkles } from 'lucide-react';

export const CaptionPlaceholder: React.FC = () => {
  return (
    <div className="rounded-2xl border border-zinc-800/90 bg-zinc-900/60 p-5 sm:p-6 backdrop-blur-sm relative overflow-hidden">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-zinc-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-zinc-800 text-amber-400">
            <Subtitles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-base text-zinc-100 flex items-center gap-2">
              <span>Burmese Captions</span>
              <span className="text-xs text-zinc-500 font-normal">(SRT & VTT Subtitles)</span>
            </h3>
            <p className="text-xs text-zinc-400">
              Synchronized timestamped captions formatted for YouTube, TikTok & Reels
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs font-medium text-amber-400 self-start sm:self-auto">
          <Lock className="w-3 h-3 text-amber-400" />
          <span>Coming Soon — Backend required</span>
        </div>
      </div>

      {/* Captions UI Preview Teaser */}
      <div className="mt-4 space-y-3">
        {/* Caption Format selector */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 p-1 bg-zinc-950/80 border border-zinc-800 rounded-lg text-xs">
            <span className="px-2.5 py-1 rounded bg-zinc-800 text-zinc-200 font-medium">SRT Format</span>
            <span className="px-2.5 py-1 text-zinc-500">WebVTT (.vtt)</span>
            <span className="px-2.5 py-1 text-zinc-500">JSON Timecodes</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              disabled
              className="px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-xs text-zinc-500 flex items-center gap-1.5 cursor-not-allowed"
            >
              <Download className="w-3 h-3" />
              <span>Download .srt</span>
            </button>
          </div>
        </div>

        {/* Preview Code Box */}
        <div className="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800/80 font-mono text-xs text-zinc-400 space-y-2 opacity-80 select-none overflow-x-auto">
          <div className="text-amber-400/80">1</div>
          <div className="text-zinc-500">00:00:01,200 --&gt; 00:00:04,800</div>
          <div className="text-zinc-200 font-burmese">
            မင်္ဂလာပါ ခင်ဗျာ။ ဒီကနေ့ ဗီဒီယိုမှာတော့ နည်းပညာ တိုးတက်မှုတွေကို တင်ပြပေးပါမယ်။
          </div>

          <div className="pt-1 text-amber-400/80">2</div>
          <div className="text-zinc-500">00:00:05,100 --&gt; 00:00:08,950</div>
          <div className="text-zinc-200 font-burmese">
            ခေတ်မီ အဆင့်မြင့် AI မော်ဒယ်တွေဟာ လူသားတွေရဲ့ စွမ်းရည်ကို မြှင့်တင်ပေးနေပါတယ်။
          </div>
        </div>

        {/* Endpoint Tag */}
        <div className="flex items-center justify-between text-[11px] font-mono text-zinc-500 pt-1">
          <span>Auto-splits sentences to 32 chars per line</span>
          <span>FastAPI: POST /api/generate-captions</span>
        </div>
      </div>
    </div>
  );
};
