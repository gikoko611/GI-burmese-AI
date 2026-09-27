import React from 'react';
import { Clock, Radio, Globe2, Volume2, Sparkles } from 'lucide-react';
import { OutputLanguage, ScriptLength, NarrationStyle } from '../types';

interface GenerationOptionsProps {
  language: OutputLanguage;
  onLanguageChange: (lang: OutputLanguage) => void;
  scriptLength: ScriptLength;
  onScriptLengthChange: (length: ScriptLength) => void;
  narrationStyle: NarrationStyle;
  onNarrationStyleChange: (style: NarrationStyle) => void;
}

const languages: OutputLanguage[] = ['Burmese', 'English'];

const scriptLengths: { value: ScriptLength; label: string; est: string }[] = [
  { value: '1 minute', label: '1 min', est: '~150 words' },
  { value: '5 minutes', label: '5 min', est: '~750 words' },
  { value: '10 minutes', label: '10 min', est: '~1,500 words' },
  { value: 'Detailed', label: 'Detailed', est: 'Complete coverage' }
];

const narrationStyles: { value: NarrationStyle; label: string; desc: string }[] = [
  { value: 'YouTube Narration', label: 'YouTube Narration', desc: 'Engaging, direct host tone' },
  { value: 'Storytelling', label: 'Storytelling', desc: 'Immersive narrative with emotional hooks' },
  { value: 'Short / TikTok', label: 'Short / TikTok', desc: 'Snappy, viral punchlines' },
  { value: 'Educational', label: 'Educational', desc: 'Authoritative, clear instruction' },
  { value: 'Detailed Explanation', label: 'Detailed Explanation', desc: 'Comprehensive depth & nuance' }
];

export const GenerationOptions: React.FC<GenerationOptionsProps> = ({
  language,
  onLanguageChange,
  scriptLength,
  onScriptLengthChange,
  narrationStyle,
  onNarrationStyleChange
}) => {
  return (
    <div className="space-y-5">
      {/* Output Language & Script Length in a responsive row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Output Language */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs sm:text-sm font-medium text-zinc-200 flex items-center gap-1.5">
              <Globe2 className="w-3.5 h-3.5 text-amber-400" />
              <span>Output Language</span>
            </label>
            <span className="text-[11px] text-zinc-500">Target dialect</span>
          </div>

          <div className="grid grid-cols-2 gap-2 p-1 bg-zinc-900/90 border border-zinc-800 rounded-xl">
            {languages.map((lang) => {
              const isActive = language === lang;
              return (
                <button
                  key={lang}
                  type="button"
                  onClick={() => onLanguageChange(lang)}
                  className={`py-2 px-3 text-xs sm:text-sm font-medium rounded-lg transition-all cursor-pointer flex items-center justify-center gap-2 ${
                    isActive
                      ? 'bg-amber-500 text-zinc-950 font-semibold shadow-sm'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                  }`}
                >
                  {lang === 'Burmese' ? (
                    <span className="font-burmese font-medium">မြန်မာ (Burmese)</span>
                  ) : (
                    <span>English</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Script Length */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs sm:text-sm font-medium text-zinc-200 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Script Length</span>
            </label>
            <span className="text-[11px] text-zinc-500">Duration estimate</span>
          </div>

          <div className="grid grid-cols-4 gap-1 p-1 bg-zinc-900/90 border border-zinc-800 rounded-xl">
            {scriptLengths.map((len) => {
              const isActive = scriptLength === len.value;
              return (
                <button
                  key={len.value}
                  type="button"
                  onClick={() => onScriptLengthChange(len.value)}
                  className={`py-2 px-1 text-center text-xs font-medium rounded-lg transition-all cursor-pointer flex flex-col items-center justify-center ${
                    isActive
                      ? 'bg-amber-500 text-zinc-950 font-semibold shadow-sm'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                  }`}
                  title={`${len.value}: ${len.est}`}
                >
                  <span className="truncate w-full">{len.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Narration Style */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-xs sm:text-sm font-medium text-zinc-200 flex items-center gap-1.5">
            <Radio className="w-3.5 h-3.5 text-amber-400" />
            <span>Narration Style</span>
          </label>
          <span className="text-[11px] text-zinc-500">Tone & pacing model</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
          {narrationStyles.map((style) => {
            const isActive = narrationStyle === style.value;
            return (
              <button
                key={style.value}
                type="button"
                onClick={() => onNarrationStyleChange(style.value)}
                className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                  isActive
                    ? 'bg-amber-500/10 border-amber-500/80 ring-1 ring-amber-500/20 text-zinc-100 shadow-sm'
                    : 'bg-zinc-900/70 border-zinc-800/80 text-zinc-400 hover:border-zinc-700 hover:bg-zinc-800/60'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className={`text-xs font-semibold ${isActive ? 'text-amber-300' : 'text-zinc-200'}`}>
                    {style.label}
                  </span>
                  {isActive && <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>}
                </div>
                <span className="text-[10px] text-zinc-500 leading-tight">
                  {style.desc}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
