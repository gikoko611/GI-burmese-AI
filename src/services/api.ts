import { ContentType, NarrationStyle, ScriptLength, OutputLanguage, GeneratedResult, VideoMetadata } from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

/**
 * Service client interface prepared for future FastAPI backend endpoints:
 * - POST /api/analyze
 * - POST /api/generate-script
 * - POST /api/generate-voice
 * - POST /api/generate-captions
 */

export interface AnalyzeVideoRequest {
  videoUrl: string;
}

export interface AnalyzeVideoResponse {
  success: boolean;
  metadata: VideoMetadata;
}

export interface GenerateScriptRequest {
  videoUrl: string;
  contentType: ContentType;
  outputLanguage: OutputLanguage;
  scriptLength: ScriptLength;
  narrationStyle: NarrationStyle;
}

export interface GenerateVoiceRequest {
  scriptId?: string;
  text: string;
  voiceModel: string;
  speed: number;
}

export interface GenerateCaptionsRequest {
  scriptId?: string;
  videoUrl: string;
  format: 'srt' | 'vtt' | 'json';
}

export async function analyzeVideo(url: string): Promise<VideoMetadata> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url,
    }),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  const data = await response.json();

  if (!data.success || !data.analysis) {
    throw new Error("Invalid analysis response from backend.");
  }

  const analysis = data.analysis;

  return {
    title: analysis.title || "YouTube Video",
    channel: analysis.channel || "Unknown Channel",
    duration: analysis.duration
      ? String(analysis.duration)
      : "Unknown",
    thumbnailUrl: `https://i.ytimg.com/vi/${analysis.videoId}/hqdefault.jpg`,
  };
}

export async function generateBurmeseScript(
  req: GenerateScriptRequest,
  onProgress?: (step: string) => void
): Promise<GeneratedResult> {
  if (onProgress) onProgress('Connecting to G.I Burmese AI backend...');

  const response = await fetch(`${API_BASE_URL}/api/generate-script`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url: req.videoUrl,
      contentType: req.contentType,
      outputLanguage: req.outputLanguage,
      scriptLength: req.scriptLength,
      narrationStyle: req.narrationStyle,
    }),
  });

  if (!response.ok) {
    let detail = `Backend error: ${response.status}`;

    try {
      const errorData = await response.json();
      if (errorData?.detail) {
        detail = errorData.detail;
      }
    } catch {
      // Keep the HTTP status message.
    }

    throw new Error(detail);
  }

  if (onProgress) onProgress('Generating Burmese narration script...');

  const data = await response.json();

  if (!data.success || !data.script) {
    throw new Error("Invalid script response from backend.");
  }

  if (onProgress) onProgress('Formatting generated script...');

  const segments = Array.isArray(data.segments) ? data.segments : [];

  return {
    title: "Generated Burmese Script",
    contentType: req.contentType,
    narrationStyle: req.narrationStyle,
    scriptLength: req.scriptLength,
    language: req.outputLanguage,
    videoUrl: req.videoUrl,
    characterCount: data.characterCount ?? 0,
    wordCount: data.wordCount ?? 0,
    estimatedDuration: data.estimatedDuration || req.scriptLength,
    fullText: data.script,
    sections: segments.map((segment: any) => ({
      timecode: segment.timestamp || undefined,
      sectionTitle: segment.heading || "Narration",
      narration: segment.content || "",
    })),
    generatedAt: new Date().toISOString(),
  };
}

