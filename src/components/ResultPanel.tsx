import React, { useState } from 'react';
import { Copy, Check, Download, FileText, Sparkles, RefreshCw, LayoutList, AlignLeft } from 'lucide-react';
import { GeneratedResult } from '../types';
import { VoicePlaceholder } from './VoicePlaceholder';
import { CaptionPlaceholder } from './CaptionPlaceholder';

interface ResultPanelProps {
  result: GeneratedResult;
  onReset?: () => void;
}

export const ResultPanel: React.FC<ResultPanelProps> = ({ result, onReset }) => {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<'sections' | 'raw'>('sections');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(result.fullText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback if clipboard API is restricted
      const textarea = document.createElement('textarea');
      textarea.value = result.fullText;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownloadTxt = () => {
    const headerInfo = `================================================
G.I Burmese AI — Generated Script
Title: ${result.title}
Content Type: ${result.contentType}
Narration Style: ${result.narrationStyle}
Script Length: ${result.scriptLength} (${result.estimatedDuration})
Language: ${result.language}
Source URL: ${result.videoUrl}
Generated: ${result.generatedAt}
Notice: Demo — AI backend not connected
================================================\n\n`;

    const contentToDownload = headerInfo + result.fullText;
    const blob = new Blob([contentToDownload], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const safeTitle = result.contentType.replace(/[^a-zA-Z0-9]/g, '_');
    link.download = `GI_Burmese_${safeTitle}_Script.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Script Result Container */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900/80 backdrop-blur-md overflow-hidden shadow-2xl shadow-black/40">
        {/* Panel Header */}
        <div className="p-4 sm:p-5 border-b border-zinc-800 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-zinc-950/60">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1.5">
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400">
                Demo — AI backend not connected
              </span>
              <span className="text-xs text-zinc-400">
                {result.contentType}
              </span>
              <span className="text-zinc-600">·</span>
              <span className="text-xs text-zinc-400">
                {result.narrationStyle}
              </span>
            </div>
            <h2 className="text-base sm:text-lg font-bold text-zinc-100 font-burmese leading-snug">
              {result.title}
            </h2>
          </div>

          {/* Quick Metrics & Actions */}
          <div className="flex flex-wrap items-center gap-2 self-start md:self-auto">
            {/* View Mode Toggle */}
            <div className="flex items-center p-0.5 bg-zinc-900 border border-zinc-800 rounded-lg mr-1">
              <button
                type="button"
                onClick={() => setViewMode('sections')}
                className={`p-1.5 rounded-md text-xs font-medium cursor-pointer transition-colors ${
                  viewMode === 'sections'
                    ? 'bg-zinc-800 text-zinc-100'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
                title="Structured Sections"
              >
                <LayoutList className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setViewMode('raw')}
                className={`p-1.5 rounded-md text-xs font-medium cursor-pointer transition-colors ${
                  viewMode === 'raw'
                    ? 'bg-zinc-800 text-zinc-100'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
                title="Full Plain Text"
              >
                <AlignLeft className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Copy Button */}
            <button
              type="button"
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700/80 active:bg-zinc-700 text-zinc-200 text-xs font-medium border border-zinc-700/60 transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Copy Script</span>
                </>
              )}
            </button>

            {/* Download TXT Button */}
            <button
              type="button"
              onClick={handleDownloadTxt}
              className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700/80 active:bg-zinc-700 text-zinc-200 text-xs font-medium border border-zinc-700/60 transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              <Download className="w-3.5 h-3.5 text-zinc-400" />
              <span>Download TXT</span>
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-5 sm:p-6 space-y-4">
          {viewMode === 'sections' ? (
            <div className="space-y-4">
              {result.sections.map((section, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-zinc-950/70 border border-zinc-800/80 space-y-2 hover:border-zinc-750 transition-colors"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-zinc-900">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-amber-500/10 text-amber-400 text-xs font-semibold flex items-center justify-center border border-amber-500/20">
                        {idx + 1}
                      </span>
                      <h3 className="font-semibold text-sm text-zinc-200">
                        {section.sectionTitle}
                      </h3>
                    </div>
                    {section.timecode && (
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                        {section.timecode}
                      </span>
                    )}
                  </div>

                  <p className="font-burmese text-sm sm:text-base text-zinc-100 leading-relaxed whitespace-pre-line pt-1">
                    {section.narration}
                  </p>

                  {section.notes && (
                    <div className="pt-2 text-xs text-zinc-400 italic flex items-center gap-1.5 bg-zinc-900/60 px-3 py-1.5 rounded-lg border border-zinc-800/50">
                      <Sparkles className="w-3 h-3 text-amber-400 shrink-0" />
                      <span>{section.notes}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/80 font-burmese text-sm sm:text-base text-zinc-100 leading-relaxed whitespace-pre-line">
              {result.fullText}
            </div>
          )}
        </div>

        {/* Panel Footer: Character count, Word count & Duration */}
        <div className="px-5 py-3.5 bg-zinc-950 border-t border-zinc-800 flex flex-wrap items-center justify-between gap-3 text-xs text-zinc-400">
          <div className="flex items-center gap-4">
            <div>
              <span className="text-zinc-500 mr-1.5">Words:</span>
              <span className="font-mono text-zinc-200 font-semibold">{result.wordCount.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-zinc-500 mr-1.5">Characters:</span>
              <span className="font-mono text-zinc-200 font-semibold">{result.characterCount.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-zinc-500 mr-1.5">Est. Duration:</span>
              <span className="font-mono text-amber-400 font-semibold">{result.estimatedDuration}</span>
            </div>
          </div>

          <div className="text-zinc-500 font-mono text-[11px]">
            Generated at {result.generatedAt}
          </div>
        </div>
      </div>

      {/* Future Sections: Burmese Voice and Burmese Captions */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 pt-2">
          <div className="h-px bg-zinc-800 flex-1"></div>
          <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">
            Future Multi-Modal Outputs
          </span>
          <div className="h-px bg-zinc-800 flex-1"></div>
        </div>

        <VoicePlaceholder scriptLength={result.scriptLength} />
        <CaptionPlaceholder />
      </div>
    </div>
  );
};
