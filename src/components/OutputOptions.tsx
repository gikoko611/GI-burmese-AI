import React from 'react';
import { FileText, Mic, Subtitles, Check } from 'lucide-react';
import { OutputFormat } from '../types';

interface OutputOptionsProps {
  selectedOutputs: OutputFormat[];
  onToggleOutput: (output: OutputFormat) => void;
}

export const OutputOptions: React.FC<OutputOptionsProps> = ({
  selectedOutputs,
  onToggleOutput
}) => {
  const isScriptSelected = selectedOutputs.includes('Burmese Script');

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-zinc-200">
          Target Outputs
        </label>
        <span className="text-xs text-zinc-500">Pipeline modules</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        {/* Burmese Script (Active & Selectable) */}
        <button
          type="button"
          onClick={() => onToggleOutput('Burmese Script')}
          className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex items-center justify-between ${
            isScriptSelected
              ? 'bg-amber-500/10 border-amber-500/80 ring-1 ring-amber-500/20 text-zinc-100'
              : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700'
          }`}
        >
          <div className="flex items-center gap-3">
            <div
              className={`p-2 rounded-lg ${
                isScriptSelected
                  ? 'bg-amber-500 text-zinc-950 font-bold'
                  : 'bg-zinc-800 text-zinc-400'
              }`}
            >
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <div className="font-semibold text-xs sm:text-sm text-zinc-100">Burmese Script</div>
              <div className="text-[11px] text-amber-400/90 font-medium">Ready in Demo</div>
            </div>
          </div>
          <div
            className={`w-5 h-5 rounded-md flex items-center justify-center border transition-colors ${
              isScriptSelected
                ? 'bg-amber-500 border-amber-500 text-zinc-950'
                : 'border-zinc-700 bg-zinc-800'
            }`}
          >
            {isScriptSelected && <Check className="w-3.5 h-3.5 stroke-[3]" />}
          </div>
        </button>

        {/* Burmese Voice (Coming Soon) */}
        <div className="p-3 rounded-xl border border-zinc-800/80 bg-zinc-900/40 opacity-75 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-zinc-800/80 text-zinc-400">
              <Mic className="w-4 h-4" />
            </div>
            <div>
              <div className="font-semibold text-xs sm:text-sm text-zinc-300">Burmese Voice</div>
              <div className="text-[11px] text-zinc-500">Audio narration synth</div>
            </div>
          </div>
          <span className="text-[11px] font-mono uppercase tracking-wider text-amber-400/90 bg-amber-400/10 border border-amber-400/20 px-2 py-0.5 rounded-md">
            Coming Soon
          </span>
        </div>

        {/* Burmese Captions (Coming Soon) */}
        <div className="p-3 rounded-xl border border-zinc-800/80 bg-zinc-900/40 opacity-75 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-zinc-800/80 text-zinc-400">
              <Subtitles className="w-4 h-4" />
            </div>
            <div>
              <div className="font-semibold text-xs sm:text-sm text-zinc-300">Burmese Captions</div>
              <div className="text-[11px] text-zinc-500">SRT / VTT Subtitles</div>
            </div>
          </div>
          <span className="text-[11px] font-mono uppercase tracking-wider text-amber-400/90 bg-amber-400/10 border border-amber-400/20 px-2 py-0.5 rounded-md">
            Coming Soon
          </span>
        </div>
      </div>
    </div>
  );
};
