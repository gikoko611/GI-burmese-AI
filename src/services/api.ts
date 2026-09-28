import {
  ContentType,
  NarrationStyle,
  ScriptLength,
  OutputLanguage,
  GeneratedResult,
  VideoMetadata,
} from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

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

export interface RecapJobResponse {
  success: boolean;
  job_id: string;
  status: string;
  message?: string | null;
}

export interface RecapStatusResponse {
  success: boolean;
  job_id: string;
  status: string;
  step?: string | null;
  progress?: number;
  message?: string | null;
  result?: {
    script?: string;
    word_count?: number;
    character_count?: number;
    estimated_duration?: string;
    video_status?: string;
    [key: string]: unknown;
  } | null;
  error?: string | null;
}

async function parseError(response: Response): Promise<string> {
  let detail = `Backend error: ${response.status}`;

  try {
    const data = await response.json();
    if (data?.detail) {
      detail = String(data.detail);
    }
  } catch {
    // Keep HTTP status message.
  }

  return detail;
}

export async function analyzeVideo(url: string): Promise<VideoMetadata> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  const data = await response.json();

  if (!data.success || !data.analysis) {
    throw new Error('Invalid analysis response from backend.');
  }

  const analysis = data.analysis;

  return {
    title: analysis.title || 'YouTube Video',
    channel: analysis.channel || 'Unknown Channel',
    duration: analysis.duration
      ? String(analysis.duration)
      : 'Unknown',
    thumbnailUrl: analysis.videoId
      ? `https://i.ytimg.com/vi/${analysis.videoId}/hqdefault.jpg`
      : '',
  };
}

export async function createRecapJob(
  videoUrl: string,
  language: string = 'my',
): Promise<RecapJobResponse> {
  const response = await fetch(`${API_BASE_URL}/api/recap`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url: videoUrl,
      language,
    }),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  const data: RecapJobResponse = await response.json();

  if (!data.success || !data.job_id) {
    throw new Error('Invalid recap job response from backend.');
  }

  return data;
}

export async function getRecapStatus(
  jobId: string,
): Promise<RecapStatusResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/recap/${encodeURIComponent(jobId)}`,
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  const data: RecapStatusResponse = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Invalid recap status response.');
  }

  return data;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function generateMovieRecap(
  videoUrl: string,
  onProgress?: (step: string) => void,
): Promise<GeneratedResult> {
  if (onProgress) {
    onProgress('Starting G.I Movie Recap pipeline...');
  }

  const job = await createRecapJob(videoUrl, 'my');

  if (onProgress) {
    onProgress(job.message || 'Recap job queued...');
  }

  while (true) {
    await sleep(2000);

    const status = await getRecapStatus(job.job_id);

    const progressText =
      status.progress !== undefined
        ? ` (${status.progress}%)`
        : '';

    if (onProgress) {
      onProgress(
        `${status.step || status.message || 'Processing recap'}${progressText}`,
      );
    }

    if (status.status === 'complete') {
      const result = status.result;

      if (!result) {
        throw new Error('Recap completed without a result.');
      }

      const script = result.script || '';

      return {
        jobId: job.job_id,
        title: 'G.I Movie Recap',
        contentType: 'Movie Recap',
        narrationStyle: 'YouTube Narration',
        scriptLength: 'Detailed',
        language: 'Burmese',
        videoUrl,
        characterCount: result.character_count ?? script.length,
        wordCount: result.word_count ?? 0,
        estimatedDuration: result.estimated_duration || 'Detailed',
        fullText: script,
        sections: [
          {
            sectionTitle: 'Burmese Movie Recap',
            narration: script,
          },
        ],
        generatedAt: new Date().toISOString(),
      };
    }

    if (status.status === 'failed') {
      throw new Error(
        status.error ||
          status.message ||
          'Movie recap generation failed.',
      );
    }
  }
}

export async function generateBurmeseScript(
  req: GenerateScriptRequest,
  onProgress?: (step: string) => void,
): Promise<GeneratedResult> {
  return generateMovieRecap(req.videoUrl, onProgress);
}


export async function uploadRecapMedia(
  jobId: string,
  file: File,
): Promise<{
  success: boolean;
  job_id: string;
  filename: string;
  media_path?: string;
  message?: string;
}> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(
    `${API_BASE_URL}/api/recap/${encodeURIComponent(jobId)}/media`,
    {
      method: 'POST',
      body: formData,
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}


export async function renderRecapVideo(
  jobId: string,
): Promise<{
  success: boolean;
  job_id: string;
  status: string;
  video?: string | null;
  duration_seconds?: number;
  segments?: number;
  message?: string | null;
}> {
  const response = await fetch(
    `${API_BASE_URL}/api/recap/${encodeURIComponent(jobId)}/render`,
    {
      method: 'POST',
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}


export function getRecapVideoUrl(jobId: string): string {
  return `${API_BASE_URL}/api/recap/${encodeURIComponent(jobId)}/video`;
}
