import React, { useState } from 'react';
import { Youtube, Search, CheckCircle2, AlertCircle, Sparkles, X } from 'lucide-react';
import { sampleVideos } from '../data/mockContent';
import { ContentType, VideoMetadata } from '../types';

interface VideoUrlInputProps {
  value: string;
  onChange: (url: string) => void;
  onSelectSample?: (url: string, type: ContentType) => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  metadata: VideoMetadata | null;
  error: string | null;
  clearError: () => void;
}

export const VideoUrlInput: React.FC<VideoUrlInputProps> = ({
  value,
  onChange,
  onSelectSample,
  onAnalyze,
  isAnalyzing,
  metadata,
  error,
  clearError
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
    if (error) clearError();
  };

  const handleClear = () => {
    onChange('');
    if (error) clearError();
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label htmlFor="youtube-url-input" className="block text-sm font-medium text-zinc-200">
          Source Video
        </label>
        <span className="text-xs text-zinc-500 font-mono">POST /api/analyze</span>
      </div>

      {/* Main Large Input Bar */}
      <div
        className={`relative flex flex-col sm:flex-row items-stretch sm:items-center rounded-xl bg-zinc-900 border transition-all duration-200 ${
          error
            ? 'border-red-500/80 ring-1 ring-red-500/30'
            : isFocused
            ? 'border-amber-500/70 ring-1 ring-amber-500/20'
            : 'border-zinc-800 hover:border-zinc-700'
        }`}
      >
        <div className="flex items-center flex-1 px-3.5 py-3">
          <Youtube className="w-5 h-5 text-red-500 shrink-0 mr-3" />
          <input
            id="youtube-url-input"
            type="text"
            value={value}
            onChange={handleInputChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Paste a YouTube video URL..."
            className="w-full bg-transparent text-sm sm:text-base text-zinc-100 placeholder-zinc-500 focus:outline-none"
          />
          {value && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1 rounded-md text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 transition-colors"
              title="Clear URL"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Analyze Video Button */}
        <div className="p-1.5 sm:pl-0">
          <button
            type="button"
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="w-full sm:w-auto px-4 py-2.5 rounded-lg bg-zinc-800 hover:bg-zinc-700/80 active:bg-zinc-700 text-zinc-100 font-medium text-sm transition-colors flex items-center justify-center gap-2 border border-zinc-700/60 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4 text-zinc-400" />
                <span>Analyze Video</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Helper text or validation error */}
      <div className="flex items-center justify-between text-xs">
        {error ? (
          <div className="flex items-center gap-1.5 text-red-400 font-medium animate-fadeIn">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>{error}</span>
          </div>
        ) : (
          <p className="text-zinc-500">Paste a video link to begin.</p>
        )}

        {metadata && (
          <div className="flex items-center gap-1 text-emerald-400 font-medium">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Video verified ({metadata.duration})</span>
          </div>
        )}
      </div>

      {/* Quick Sample Links for convenient 1-click testing */}
      <div className="pt-1">
        <span className="text-xs text-zinc-500 block mb-1.5 font-medium">Or try quick sample demo links:</span>
        <div className="flex flex-wrap gap-2">
          {sampleVideos.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                if (onSelectSample) {
                  onSelectSample(sample.url, sample.type);
                } else {
                  onChange(sample.url);
                }
              }}
              className="text-left text-xs px-2.5 py-1.5 rounded-lg bg-zinc-900/90 border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors flex items-center gap-1.5"
            >
              <Sparkles className="w-3 h-3 text-amber-400 shrink-0" />
              <span className="truncate max-w-[200px]">{sample.title}</span>
              <span className="text-[10px] text-zinc-500 border-l border-zinc-800 pl-1.5">{sample.type}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
