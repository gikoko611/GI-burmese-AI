import { ContentType, NarrationStyle, ScriptLength, OutputLanguage, GeneratedResult, VideoMetadata } from '../types';
import { generateMockResult } from '../data/mockContent';

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
  // Simulates POST /api/analyze
  await new Promise(resolve => setTimeout(resolve, 800));

  // Extract a simulated title if it's a known or parsed URL
  let detectedTitle = 'YouTube Video Content';
  if (url.includes('youtu')) {
    detectedTitle = 'Extracted Video: ' + (url.split('v=')[1]?.slice(0, 11) || 'Streaming Source');
  }

  return {
    title: detectedTitle,
    channel: 'Verified Creator',
    duration: '12:30',
    thumbnailUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80'
  };
}

export async function generateBurmeseScript(
  req: GenerateScriptRequest,
  onProgress?: (step: string) => void
): Promise<GeneratedResult> {
  // Simulates POST /api/generate-script with progressive steps
  if (onProgress) onProgress('Connecting to video metadata stream...');
  await new Promise(resolve => setTimeout(resolve, 600));

  if (onProgress) onProgress('Extracting transcript & key narrative points...');
  await new Promise(resolve => setTimeout(resolve, 700));

  if (onProgress) onProgress('Translating & adapting nuances into natural Burmese...');
  await new Promise(resolve => setTimeout(resolve, 700));

  if (onProgress) onProgress(`Formatting for ${req.narrationStyle} cadence (${req.scriptLength})...`);
  await new Promise(resolve => setTimeout(resolve, 500));

  return generateMockResult(
    req.videoUrl,
    req.contentType,
    req.narrationStyle,
    req.scriptLength,
    req.outputLanguage
  );
}
