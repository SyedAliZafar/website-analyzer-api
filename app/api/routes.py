from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional
from app.services.analyzer import WebsiteAnalyzer
from app.models.schemas import AnalysisResult
import uuid

router = APIRouter()
analyzer = WebsiteAnalyzer()

# In-memory storage for analysis results
analysis_results: Dict[str, Optional[AnalysisResult]] = {}


class AnalyzeRequest(BaseModel):
    url: str
    analyze_desktop: bool = True
    analyze_mobile: bool = True


async def run_analysis(analysis_id: str, url: str, analyze_desktop: bool, analyze_mobile: bool):
    """Background task to run the analysis"""
    try:
        result = await analyzer.analyze(
            url=url,
            analyze_desktop=analyze_desktop,
            analyze_mobile=analyze_mobile
        )
        analysis_results[analysis_id] = result
    except Exception as e:
        # Store error result
        from datetime import datetime
        from app.models.schemas import AnalysisStatus
        analysis_results[analysis_id] = AnalysisResult(
            id=analysis_id,
            url=url,
            status=AnalysisStatus.FAILED,
            timestamp=datetime.utcnow(),
            error_message=str(e)
        )


@router.post("/analyze")
async def analyze_website(payload: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Start website analysis and return analysis ID
    """
    if not payload.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    analysis_id = str(uuid.uuid4())
    analysis_results[analysis_id] = None  # Mark as pending
    
    # Run analysis in background
    background_tasks.add_task(
        run_analysis,
        analysis_id,
        payload.url,
        payload.analyze_desktop,
        payload.analyze_mobile
    )
    
    return {"analysis_id": analysis_id}


@router.get("/analyze/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """
    Get analysis result by ID
    """
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id]
    
    if result is None:
        # Analysis is still pending
        return {"status": "pending", "analysis_id": analysis_id}
    
    return result