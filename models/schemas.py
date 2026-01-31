"""
Pydantic models and enums used across the Website Analyzer API.
Single source of truth for request/response schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List

from pydantic import BaseModel, HttpUrl, Field


# ============================================================================
# Enums
# ============================================================================

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"


# ============================================================================
# Request Models
# ============================================================================

class AnalysisRequest(BaseModel):
    url: HttpUrl
    analyze_mobile: bool = True
    analyze_desktop: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.example.com",
                "analyze_mobile": True,
                "analyze_desktop": True,
            }
        }


# ============================================================================
# Analysis Models
# ============================================================================

class PerformanceMetrics(BaseModel):
    score: float = Field(..., ge=0, le=100)
    first_contentful_paint: Optional[float] = None
    speed_index: Optional[float] = None
    largest_contentful_paint: Optional[float] = None
    time_to_interactive: Optional[float] = None
    total_blocking_time: Optional[float] = None
    cumulative_layout_shift: Optional[float] = None


class SEOAnalysis(BaseModel):
    score: float = Field(..., ge=0, le=100)
    title: Optional[str] = None
    title_length: Optional[int] = None
    meta_description: Optional[str] = None
    meta_description_length: Optional[int] = None
    h1_tags: List[str] = []
    h2_tags: List[str] = []
    canonical_url: Optional[str] = None
    meta_robots: Optional[str] = None
    open_graph_tags: Dict[str, str] = {}
    structured_data: bool = False
    image_alt_tags_missing: int = 0
    total_images: int = 0


class ContentAnalysis(BaseModel):
    word_count: int
    paragraph_count: int
    heading_structure_score: float
    readability_score: float
    keyword_density: Dict[str, float] = {}
    internal_links: int = 0
    external_links: int = 0
    broken_links: int = 0
    content_gaps: List[str] = []


class Recommendation(BaseModel):
    category: str
    priority: str  # high, medium, low
    issue: str
    suggestion: str
    impact: str


class AIInsights(BaseModel):
    summary: str
    strengths: List[str] = []
    weaknesses: List[str] = []
    quick_wins: List[str] = []
    strategic_recommendations: str = ""


class DeviceAnalysis(BaseModel):
    device_type: DeviceType
    performance: PerformanceMetrics
    seo: SEOAnalysis
    content: ContentAnalysis
    recommendations: List[Recommendation] = []


# ============================================================================
# Response Models
# ============================================================================

class AnalysisResult(BaseModel):
    id: str
    url: str
    status: AnalysisStatus
    timestamp: datetime
    desktop: Optional[DeviceAnalysis] = None
    mobile: Optional[DeviceAnalysis] = None
    overall_score: Optional[float] = None
    ai_insights: Optional[AIInsights] = None
    error_message: Optional[str] = None
