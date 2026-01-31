"""
API routes for the Website Analyzer.
Thin routing layer delegating logic to services.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalysisRequest, AnalysisResult
from app.services.analyzer import WebsiteAnalyzer

router = APIRouter()
analyzer = WebsiteAnalyzer()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_website(request: AnalysisRequest) -> AnalysisResult:
    """
    Analyze a website for performance, SEO, content, and AI insights.
    """
    try:
        return await analyzer.analyze(
            url=str(request.url),
            analyze_desktop=request.analyze_desktop,
            analyze_mobile=request.analyze_mobile,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
