from typing import List, Optional

from pydantic import BaseModel, Field


class AnalyzeVideoRequest(BaseModel):
    url: str = Field(..., min_length=1)


class VideoAnalysisResult(BaseModel):
    videoId: str
    title: str
    duration: Optional[str] = None
    channel: Optional[str] = None
    detectedTopics: List[str] = []
    suggestedContentType: Optional[str] = None
    isDemoMode: bool = True
    disclaimer: Optional[str] = None


class AnalyzeVideoResponse(BaseModel):
    success: bool
    analysis: VideoAnalysisResult


class GenerateScriptRequest(BaseModel):
    url: str
    contentType: str
    scriptLength: str
    narrationStyle: str
    outputLanguage: str
    analysis: Optional[VideoAnalysisResult] = None


class ScriptSegment(BaseModel):
    timestamp: str
    heading: str
    content: str


class GenerateScriptResponse(BaseModel):
    success: bool
    script: str
    segments: List[ScriptSegment] = []
    wordCount: int = 0
    characterCount: int = 0
    estimatedDuration: Optional[str] = None
    isDemoMode: bool = True
    disclaimer: Optional[str] = None


class GenerateVoiceRequest(BaseModel):
    script: str
    language: str = "my"


class GenerateVoiceResponse(BaseModel):
    success: bool
    configured: bool = False
    message: str
    audioUrl: Optional[str] = None


class GenerateCaptionsRequest(BaseModel):
    script: str
    language: str = "my"


class GenerateCaptionsResponse(BaseModel):
    success: bool
    configured: bool = False
    message: str
    srt: Optional[str] = None
    vtt: Optional[str] = None


class RecapRequest(BaseModel):
    url: str = Field(..., min_length=1)
    language: str = "my"


class RecapJobResponse(BaseModel):
    success: bool
    job_id: str
    status: str
    message: Optional[str] = None


class RecapStatusResponse(BaseModel):
    success: bool
    job_id: str
    status: str
    step: Optional[str] = None
    progress: int = 0
    message: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
