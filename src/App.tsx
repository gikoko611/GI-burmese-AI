/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { VideoUrlInput } from './components/VideoUrlInput';
import { ContentTypeSelector } from './components/ContentTypeSelector';
import { GenerationOptions } from './components/GenerationOptions';
import { OutputOptions } from './components/OutputOptions';
import { GenerateButton } from './components/GenerateButton';
import { ResultPanel } from './components/ResultPanel';
import {
  ContentType,
  OutputLanguage,
  ScriptLength,
  NarrationStyle,
  OutputFormat,
  GeneratedResult,
  VideoMetadata
} from './types';
import { analyzeVideo, generateBurmeseScript, uploadRecapMedia, renderRecapVideo, getRecapVideoUrl } from './services/api';
import { Sparkles, Terminal, FileCode2, ArrowUpRight, Upload, Film, Play, Download, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

export default function App() {
  // Input state
  const [videoUrl, setVideoUrl] = useState('');
  const [urlError, setUrlError] = useState<string | null>(null);

  // Configuration options
  const [contentType, setContentType] = useState<ContentType>('Technology');
  const [outputLanguage, setOutputLanguage] = useState<OutputLanguage>('Burmese');
  const [scriptLength, setScriptLength] = useState<ScriptLength>('5 minutes');
  const [narrationStyle, setNarrationStyle] = useState<NarrationStyle>('YouTube Narration');
  const [selectedOutputs, setSelectedOutputs] = useState<OutputFormat[]>(['Burmese Script']);

  // Async states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [videoMetadata, setVideoMetadata] = useState<VideoMetadata | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState<string>('');
  const [result, setResult] = useState<GeneratedResult | null>(null);
  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [isUploadingMedia, setIsUploadingMedia] = useState(false);
  const [isRenderingVideo, setIsRenderingVideo] = useState(false);
  const [videoReady, setVideoReady] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);

  // Handle URL change
  const handleUrlChange = (url: string) => {
    setVideoUrl(url);
    if (urlError) setUrlError(null);
  };

  // Sample quick picker
  const handleSelectSample = (sampleUrl: string, sampleType: ContentType) => {
    setVideoUrl(sampleUrl);
    setContentType(sampleType);
    setUrlError(null);
  };

  // Toggle output module
  const handleToggleOutput = (output: OutputFormat) => {
    if (output === 'Burmese Script') {
      // Must keep at least Burmese Script active
      return;
    }
  };

  // Analyze video action
  const handleAnalyze = async () => {
    if (!videoUrl.trim()) {
      setUrlError('Please enter a video URL first.');
      return;
    }

    setUrlError(null);
    setIsAnalyzing(true);
    try {
      const data = await analyzeVideo(videoUrl);
      setVideoMetadata(data);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : 'Failed to analyze video URL.';
      setUrlError(message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Generate Burmese Content action
  const handleGenerate = async () => {
    if (!videoUrl.trim()) {
      setUrlError('Please enter a video URL first.');
      // Scroll to video input smoothly if on mobile
      const el = document.getElementById('youtube-url-input');
      el?.focus();
      return;
    }

    setUrlError(null);
    setIsGenerating(true);
    setGenerationStep('Initializing pipeline...');

    try {
      const generated = await generateBurmeseScript(
        {
          videoUrl: videoUrl.trim(),
          contentType,
          outputLanguage,
          scriptLength,
          narrationStyle
        },
        (step) => setGenerationStep(step)
      );
      setResult(generated);

      // Scroll to results gently
      setTimeout(() => {
        const resultsEl = document.getElementById('generation-results');
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } catch {
      setUrlError('An error occurred during script generation.');
    } finally {
      setIsGenerating(false);
      setGenerationStep('');
    }
  };

  const handleUploadMedia = async () => {
    if (!result?.jobId) {
      setVideoError('No recap job is available. Generate the recap first.');
      return;
    }

    if (!mediaFile) {
      setVideoError('Please select an authorized video file first.');
      return;
    }

    setVideoError(null);
    setVideoReady(false);
    setIsUploadingMedia(true);

    try {
      await uploadRecapMedia(result.jobId, mediaFile);
    } catch (error) {
      setVideoError(
        error instanceof Error
          ? error.message
          : 'Failed to upload video media.',
      );
    } finally {
      setIsUploadingMedia(false);
    }
  };

  const handleRenderVideo = async () => {
    if (!result?.jobId) {
      setVideoError('No recap job is available. Generate the recap first.');
      return;
    }

    setVideoError(null);
    setIsRenderingVideo(true);
    setVideoReady(false);

    try {
      await renderRecapVideo(result.jobId);
      setVideoReady(true);
    } catch (error) {
      setVideoError(
        error instanceof Error
          ? error.message
          : 'Failed to render recap video.',
      );
    } finally {
      setIsRenderingVideo(false);
    }
  };

  const handleMediaFileChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0] ?? null;
    setMediaFile(file);
    setVideoReady(false);
    setVideoError(null);
  };

  const recapVideoUrl = result?.jobId
    ? getRecapVideoUrl(result.jobId)
    : null;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-amber-500/20 selection:text-amber-200">
      {/* App Header */}
      <Header />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Hero Section */}
        <Hero />

        {/* 2-Column Desktop Grid / Stacked Mobile Layout */}
        <div className="mt-6 lg:mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Form & Configuration (5 cols on lg) */}
          <div className="lg:col-span-6 xl:col-span-5 space-y-6">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5 sm:p-6 backdrop-blur-sm space-y-6">
              {/* Video URL Section */}
              <VideoUrlInput
                value={videoUrl}
                onChange={handleUrlChange}
                onSelectSample={handleSelectSample}
                onAnalyze={handleAnalyze}
                isAnalyzing={isAnalyzing}
                metadata={videoMetadata}
                error={urlError}
                clearError={() => setUrlError(null)}
              />

              <div className="h-px bg-zinc-800/80"></div>

              {/* Content Type Selector */}
              <ContentTypeSelector
                selected={contentType}
                onSelect={setContentType}
              />

              <div className="h-px bg-zinc-800/80"></div>

              {/* Generation Options (Language, Length, Narration Style) */}
              <GenerationOptions
                language={outputLanguage}
                onLanguageChange={setOutputLanguage}
                scriptLength={scriptLength}
                onScriptLengthChange={setScriptLength}
                narrationStyle={narrationStyle}
                onNarrationStyleChange={setNarrationStyle}
              />

              <div className="h-px bg-zinc-800/80"></div>

              {/* Output Pipeline Options */}
              <OutputOptions
                selectedOutputs={selectedOutputs}
                onToggleOutput={handleToggleOutput}
              />

              {/* Primary Action Button */}
              <div className="pt-2">
                <GenerateButton
                  onClick={handleGenerate}
                  isLoading={isGenerating}
                  loadingStep={generationStep}
                />
              </div>
            </div>

            {/* Backend Status */}
            <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/30 p-4 text-xs text-zinc-400 space-y-2">
              <div className="flex items-center justify-between text-zinc-300 font-medium">
                <span className="flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-amber-400" />
                  <span>G.I Backend Connected</span>
                </span>
                <span className="font-mono text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                  Production Ready
                </span>
              </div>
              <p className="text-zinc-500 leading-relaxed">
                Frontend types and API wrappers in <code className="text-zinc-300 bg-zinc-800/80 px-1 py-0.5 rounded">src/services/api.ts</code> are wired for:
              </p>
              <div className="grid grid-cols-2 gap-1.5 font-mono text-[11px] text-zinc-400 pt-1">
                <div className="bg-zinc-950/70 p-1.5 rounded border border-zinc-800/70">
                  POST /api/analyze
                </div>
                <div className="bg-zinc-950/70 p-1.5 rounded border border-zinc-800/70">
                  POST /api/generate-script
                </div>
                <div className="bg-zinc-950/70 p-1.5 rounded border border-zinc-800/70">
                  POST /api/generate-voice
                </div>
                <div className="bg-zinc-950/70 p-1.5 rounded border border-zinc-800/70">
                  POST /api/generate-captions
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Output & Generation Preview (7 cols on lg) */}
          {result && (
            <div className="lg:col-span-6 xl:col-span-7 rounded-2xl border border-zinc-800 bg-zinc-900/70 p-5 shadow-xl">
              <div className="mb-5 flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Film className="h-5 w-5 text-amber-400" />
                    <h2 className="text-lg font-semibold text-zinc-100">
                      Video Production
                    </h2>
                  </div>
                  <p className="mt-1 text-sm text-zinc-400">
                    Upload authorized media and render your Burmese recap video.
                  </p>
                </div>

                {videoReady && (
                  <div className="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
                    <CheckCircle2 className="h-4 w-4" />
                    Ready
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <label
                  htmlFor="recap-media-upload"
                  className="flex cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-zinc-700 bg-zinc-950/60 px-5 py-7 text-center transition hover:border-amber-500/50 hover:bg-zinc-950"
                >
                  <Upload className="mb-3 h-7 w-7 text-zinc-400" />

                  <span className="text-sm font-medium text-zinc-200">
                    {mediaFile
                      ? mediaFile.name
                      : 'Choose authorized video media'}
                  </span>

                  <span className="mt-1 text-xs text-zinc-500">
                    MP4, MOV, MKV, WEBM or AVI
                  </span>

                  <input
                    id="recap-media-upload"
                    type="file"
                    accept=".mp4,.mov,.mkv,.webm,.avi,video/*"
                    className="hidden"
                    onChange={handleMediaFileChange}
                  />
                </label>

                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <button
                    type="button"
                    onClick={handleUploadMedia}
                    disabled={
                      !mediaFile ||
                      isUploadingMedia ||
                      isRenderingVideo
                    }
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-zinc-700 bg-zinc-800 px-4 py-3 text-sm font-semibold text-zinc-100 transition hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {isUploadingMedia ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Upload className="h-4 w-4" />
                    )}
                    {isUploadingMedia ? 'Uploading...' : 'Upload Media'}
                  </button>

                  <button
                    type="button"
                    onClick={handleRenderVideo}
                    disabled={
                      !result.jobId ||
                      isUploadingMedia ||
                      isRenderingVideo
                    }
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-amber-500 px-4 py-3 text-sm font-semibold text-zinc-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {isRenderingVideo ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Film className="h-4 w-4" />
                    )}
                    {isRenderingVideo
                      ? 'Rendering...'
                      : 'Render Recap Video'}
                  </button>
                </div>

                {videoError && (
                  <div className="flex items-start gap-2 rounded-xl border border-red-900/60 bg-red-950/30 px-4 py-3 text-sm text-red-300">
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                    <span>{videoError}</span>
                  </div>
                )}

                {videoReady && recapVideoUrl && (
                  <div className="overflow-hidden rounded-xl border border-zinc-800 bg-black">
                    <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
                      <div className="flex items-center gap-2 text-sm font-medium text-zinc-200">
                        <Play className="h-4 w-4 text-amber-400" />
                        Rendered Recap
                      </div>

                      <a
                        href={recapVideoUrl}
                        download="gi-burmese-recap.mp4"
                        className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-700 px-3 py-1.5 text-xs font-semibold text-zinc-200 transition hover:bg-zinc-800"
                      >
                        <Download className="h-3.5 w-3.5" />
                        Download MP4
                      </a>
                    </div>

                    <video
                      controls
                      playsInline
                      preload="metadata"
                      src={recapVideoUrl}
                      className="aspect-video w-full bg-black"
                    >
                      Your browser does not support HTML5 video.
                    </video>
                  </div>
                )}

                <p className="text-xs leading-relaxed text-zinc-500">
                  Only upload video media you are authorized to use. G.I does
                  not automatically download copyrighted movie files.
                </p>
              </div>
            </div>
          )}

          <div id="generation-results" className="lg:col-span-6 xl:col-span-7">
            {result ? (
              <ResultPanel
                result={result}
                onReset={() => {
                  setResult(null);
                  setVideoUrl('');
                }}
              />
            ) : (
              /* Initial Empty State / Onboarding Guide */
              <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/30 p-8 sm:p-10 text-center flex flex-col items-center justify-center min-h-[500px]">
                <div className="w-14 h-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-amber-400 mb-4 shadow-inner">
                  <Sparkles className="w-7 h-7" />
                </div>

                <h3 className="text-lg sm:text-xl font-bold text-zinc-100 tracking-tight">
                  Burmese Script Generation Workspace
                </h3>
                <p className="mt-2 text-sm text-zinc-400 max-w-md mx-auto leading-relaxed">
                  Paste any YouTube URL or choose a demo video on the left, pick your target style and duration, and click <span className="text-amber-400 font-semibold">Generate Burmese Content</span>.
                </p>

                {/* Feature preview cards */}
                <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-xl text-left">
                  <div className="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80">
                    <div className="text-xs font-semibold text-zinc-200 mb-1">
                      1. Video Extraction
                    </div>
                    <div className="text-[11px] text-zinc-400">
                      Transcribes speech & timestamps with scene awareness.
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80">
                    <div className="text-xs font-semibold text-zinc-200 mb-1">
                      2. Burmese Nuance
                    </div>
                    <div className="text-[11px] text-zinc-400">
                      Adapts tone into natural spoken Myanmar phrasing.
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80">
                    <div className="text-xs font-semibold text-zinc-200 mb-1">
                      3. Multi-Channel
                    </div>
                    <div className="text-[11px] text-zinc-400">
                      Outputs script, ready for future Voice and Captions.
                    </div>
                  </div>
                </div>

                {/* Instant Try Button */}
                <div className="mt-8">
                  <button
                    type="button"
                    onClick={() => {
                      handleSelectSample(
                        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        'Technology'
                      );
                      setTimeout(() => {
                        handleGenerate();
                      }, 200);
                    }}
                    className="px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-xs sm:text-sm font-medium text-amber-400 transition-colors inline-flex items-center gap-2 cursor-pointer"
                  >
                    <span>Load & Run Sample Tech Video</span>
                    <ArrowUpRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-zinc-900 bg-zinc-950/90 py-6 text-center text-xs text-zinc-500 mt-12">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-zinc-400">G.I Burmese AI</span>
            <span>·</span>
            <span>Original Burmese Content Engine</span>
          </div>

          <div className="flex items-center gap-4 text-zinc-400">
            <span>Cloud AI Mode</span>
            <span>·</span>
            <span>Secure Backend API</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
