export type ContentType =
  | 'Movie Recap'
  | 'Tutorial / How-to'
  | 'Tips & Tricks'
  | 'Technology'
  | 'Educational'
  | 'General Explanation';

export type OutputLanguage = 'Burmese' | 'English';

export type ScriptLength = '1 minute' | '5 minutes' | '10 minutes' | 'Detailed';

export type NarrationStyle =
  | 'YouTube Narration'
  | 'Storytelling'
  | 'Short / TikTok'
  | 'Educational'
  | 'Detailed Explanation';

export type OutputFormat = 'Burmese Script' | 'Burmese Voice' | 'Burmese Captions';

export interface GenerationConfig {
  videoUrl: string;
  contentType: ContentType;
  outputLanguage: OutputLanguage;
  scriptLength: ScriptLength;
  narrationStyle: NarrationStyle;
  selectedOutputs: OutputFormat[];
}

export interface ScriptSection {
  timecode?: string;
  sectionTitle: string;
  narration: string;
  notes?: string;
}

export interface GeneratedResult {
  title: string;
  contentType: ContentType;
  narrationStyle: NarrationStyle;
  scriptLength: ScriptLength;
  language: OutputLanguage;
  videoUrl: string;
  characterCount: number;
  wordCount: number;
  estimatedDuration: string;
  fullText: string;
  sections: ScriptSection[];
  generatedAt: string;
}

export interface VideoMetadata {
  title: string;
  channel: string;
  duration: string;
  thumbnailUrl: string;
}
