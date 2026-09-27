import React from 'react';
import { Mic, Lock, Play, Volume2, Sliders, AudioWaveform } from 'lucide-react';

interface VoicePlaceholderProps {
  scriptLength?: string;
}

export const VoicePlaceholder: React.FC<VoicePlaceholderProps> = ({ scriptLength }) => {
  return (
    <div className="rounded-2xl border border-zinc-800/90 bg-zinc-900/60 p-5 sm:p-6 backdrop-blur-sm relative overflow-hidden">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-zinc-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-zinc-800 text-amber-400">
            <Mic className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-base text-zinc-100 flex items-center gap-2">
              <span>Burmese Voice</span>
              <span className="text-xs text-zinc-500 font-normal">(TTS Audio Narration)</span>
            </h3>
            <p className="text-xs text-zinc-400">
              Natural neural voice synthesis in Burmese accent & cadence
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs font-medium text-amber-400 self-start sm:self-auto">
          <Lock className="w-3 h-3 text-amber-400" />
          <span>Coming Soon — Backend required</span>
        </div>
      </div>

      {/* Voice Synthesis UI Preview Teaser */}
      <div className="mt-4 space-y-4">
        {/* Voice Selector Mockup */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="p-3 rounded-xl bg-zinc-950/60 border border-zinc-800/80 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-amber-500/20 text-amber-300 flex items-center justify-center text-xs font-bold">
                MT
              </div>
              <div>
                <div className="text-xs font-semibold text-zinc-200">မင်းသန့် (Min Thant)</div>
                <div className="text-[11px] text-zinc-500">Natural Male · Studio Narration</div>
              </div>
            </div>
            <span className="text-[10px] text-zinc-400 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800">
              Default
            </span>
          </div>

          <div className="p-3 rounded-xl bg-zinc-950/60 border border-zinc-800/80 flex items-center justify-between opacity-70">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-zinc-800 text-zinc-400 flex items-center justify-center text-xs font-bold">
                SM
              </div>
              <div>
                <div className="text-xs font-semibold text-zinc-300">စုမြတ် (Su Myat)</div>
                <div className="text-[11px] text-zinc-500">Warm Female · Storytelling</div>
              </div>
            </div>
            <span className="text-[10px] text-zinc-500">Preset</span>
          </div>
        </div>

        {/* Synthesizer Audio Player Stub */}
        <div className="p-4 rounded-xl bg-zinc-950/90 border border-zinc-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              disabled
              type="button"
              className="w-10 h-10 rounded-full bg-zinc-800 text-zinc-500 flex items-center justify-center cursor-not-allowed border border-zinc-700/50 shrink-0"
              title="Requires backend connection"
            >
              <Play className="w-4 h-4 ml-0.5 fill-current" />
            </button>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-zinc-400">00:00</span>
                <span className="text-zinc-600">/</span>
                <span className="text-xs font-mono text-zinc-500">
                  {scriptLength === '1 minute' ? '01:00' : '04:45'}
                </span>
              </div>
              <div className="text-[11px] text-zinc-500">MP3 320kbps Studio Master</div>
            </div>
          </div>

          {/* Waveform graphic visualization */}
          <div className="flex items-center gap-1 h-7 w-full sm:w-48 justify-center opacity-40">
            {[40, 65, 85, 30, 95, 75, 45, 90, 60, 100, 70, 45, 80, 50, 35, 90, 65, 30, 75, 40].map((h, i) => (
              <span
                key={i}
                style={{ height: `${h}%` }}
                className="w-1 rounded-full bg-amber-400"
              ></span>
            ))}
          </div>

          {/* Endpoint Tag */}
          <div className="text-right w-full sm:w-auto">
            <span className="text-[11px] font-mono text-zinc-500 block">
              FastAPI: POST /api/generate-voice
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
