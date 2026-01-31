"""
WebsiteAnalyzer orchestrates performance, SEO, content, and AI analysis.
This service coordinates all lower-level services and utilities.
"""

import uuid
from datetime import datetime
import httpx

from app.core.logging import get_logger
from app.models.schemas import (
    AnalysisResult,
    AnalysisStatus,
    DeviceAnalysis,
    DeviceType,
)
from app.services.pagespeed import PageSpeedService
from app.services.gemini import GeminiAnalyzer
from app.utils.seo import analyze_seo
from app.utils.content import analyze_content

logger = get_logger(__name__)


class WebsiteAnalyzer:
    def __init__(self) -> None:
        self.pagespeed = PageSpeedService()
        self.gemini = GeminiAnalyzer()

    async def analyze(self, url: str, analyze_desktop: bool, analyze_mobile: bool) -> AnalysisResult:
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting analysis {analysis_id} for {url}")

        try:
            html = await self._fetch_html(url)

            desktop = None
            mobile = None
            scores = []

            if analyze_desktop:
                desktop = await self._analyze_device(url, html, DeviceType.DESKTOP)
                scores.append(desktop.performance.score)

            if analyze_mobile:
                mobile = await self._analyze_device(url, html, DeviceType.MOBILE)
                scores.append(mobile.performance.score)

            overall_score = round(sum(scores) / len(scores), 1) if scores else None

            ai_insights = await self.gemini.generate_insights(
                url=url,
                desktop=desktop,
                mobile=mobile,
                overall_score=overall_score or 0,
            )

            return AnalysisResult(
                id=analysis_id,
                url=url,
                status=AnalysisStatus.COMPLETED,
                timestamp=datetime.utcnow(),
                desktop=desktop,
                mobile=mobile,
                overall_score=overall_score,
                ai_insights=ai_insights,
            )

        except Exception as exc:
            logger.exception("Analysis failed")
            return AnalysisResult(
                id=analysis_id,
                url=url,
                status=AnalysisStatus.FAILED,
                timestamp=datetime.utcnow(),
                error_message=str(exc),
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    async def _analyze_device(self, url: str, html: str, device: DeviceType) -> DeviceAnalysis:
        performance = await self.pagespeed.analyze(url, device)
        seo = analyze_seo(html, url)
        content = analyze_content(html, url)

        return DeviceAnalysis(
            device_type=device,
            performance=performance,
            seo=seo,
            content=content,
            recommendations=[],
        )
