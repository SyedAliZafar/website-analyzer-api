"""
WebsiteAnalyzer orchestrates performance, SEO, content, and AI analysis.
This service coordinates all lower-level services and utilities.
"""

import uuid
from datetime import datetime
import httpx
import asyncio

from app.core.logging import get_logger
from app.models.schemas import (
    AnalysisResult,
    AnalysisStatus,
    DeviceAnalysis,
    DeviceType,
)
from app.services.pagespeed import PageSpeedService
from app.services.gemini import GeminiAnalyzer
#from app.services.deepseek import DeepSeekAnalyzer
from app.utils.seo import analyze_seo
from app.utils.content import analyze_content

logger = get_logger(__name__)


class WebsiteAnalyzer:
    def __init__(self) -> None:
        self.pagespeed = PageSpeedService()
        #self.gemini = DeepSeekAnalyzer()
        self.gemini = GeminiAnalyzer()

    async def analyze(self, url: str, analyze_desktop: bool, analyze_mobile: bool) -> AnalysisResult:
        analysis_id = str(uuid.uuid4())
        logger.info(f"🚀 Starting analysis {analysis_id} for {url}")

        try:
            # Fetch HTML
            logger.info(f"📄 Fetching HTML from {url}")
            html = await self._fetch_html(url)
            logger.info(f"✅ HTML fetched successfully ({len(html)} bytes)")

            desktop = None
            mobile = None
            scores = []

            # Analyze desktop
            if analyze_desktop:
                logger.info("🖥️ Starting desktop analysis")
                desktop = await self._analyze_device(url, html, DeviceType.DESKTOP)
                scores.append(desktop.performance.score)
                logger.info(f"✅ Desktop analysis complete (score: {desktop.performance.score})")

            # Analyze mobile
            if analyze_mobile:
                logger.info("📱 Starting mobile analysis")
                mobile = await self._analyze_device(url, html, DeviceType.MOBILE)
                scores.append(mobile.performance.score)
                logger.info(f"✅ Mobile analysis complete (score: {mobile.performance.score})")

            # Calculate overall score
            overall_score = round(sum(scores) / len(scores), 1) if scores else None
            logger.info(f"📊 Overall score: {overall_score}")

            # Generate AI insights with timeout protection
            logger.info("🤖 Generating AI insights...")
            try:
                ai_insights = await asyncio.wait_for(
                    self.gemini.generate_insights(
                        url=url,
                        desktop=desktop,
                        mobile=mobile,
                        overall_score=overall_score or 0,
                    ),
                    timeout=45.0  # 45 second overall timeout for AI insights
                )
                logger.info("✅ AI insights generated successfully")
            except asyncio.TimeoutError:
                logger.error("⏱️ AI insights generation timed out, using fallback")
                from app.models.schemas import AIInsights
                ai_insights = AIInsights(
                    summary=f"Website scored {overall_score}/100. Analysis timed out.",
                    strengths=["Performance and SEO metrics collected"],
                    weaknesses=["AI analysis timed out"],
                    quick_wins=["Review the metrics below"],
                    strategic_recommendations="Try again or check API configuration."
                )
            except Exception as exc:
                logger.error(f"❌ AI insights generation failed: {exc}", exc_info=True)
                from app.models.schemas import AIInsights
                ai_insights = AIInsights(
                    summary=f"Website scored {overall_score}/100. AI insights unavailable.",
                    strengths=["Performance and SEO metrics collected"],
                    weaknesses=["AI analysis failed"],
                    quick_wins=["Review the metrics below"],
                    strategic_recommendations="Check logs for details."
                )

            logger.info(f"✅ Analysis {analysis_id} completed successfully")

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
            logger.exception(f"❌ Analysis {analysis_id} failed")
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
        logger.info(f"Analyzing {device.value} device")
        
        # Run performance analysis
        performance = await self.pagespeed.analyze(url, device)
        
        # Run SEO analysis
        seo = analyze_seo(html, url)
        
        # Run content analysis
        content = analyze_content(html, url)

        return DeviceAnalysis(
            device_type=device,
            performance=performance,
            seo=seo,
            content=content,
            recommendations=[],
        )