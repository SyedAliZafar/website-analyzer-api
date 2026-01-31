"""
Gemini AI service for generating high-level website insights.
Provides graceful fallback when API key is not configured or errors occur.
"""

import json
import asyncio
from typing import Optional

import google.generativeai as genai

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import DeviceAnalysis, AIInsights

logger = get_logger(__name__)
settings = get_settings()


class GeminiAnalyzer:
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.model = None

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured. AI insights will be basic.")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-pro")
            logger.info("Gemini AI initialized successfully")
        except Exception as exc:
            logger.error(f"Failed to initialize Gemini AI: {exc}")
            self.model = None

    async def generate_insights(
        self,
        url: str,
        desktop: Optional[DeviceAnalysis],
        mobile: Optional[DeviceAnalysis],
        overall_score: float,
    ) -> AIInsights:
        """
        Generate AI-powered insights using Gemini.
        Falls back to basic insights if Gemini is unavailable.
        """

        if not self.model:
            return self._fallback_insights(overall_score)

        try:
            prompt = self._build_prompt(url, desktop, mobile, overall_score)

            logger.info("Sending request to Gemini AI")
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
            )

            response_text = response.text.strip()
            response_text = self._strip_code_fences(response_text)

            insights_data = json.loads(response_text)
            return AIInsights(**insights_data)

        except Exception as exc:
            logger.error(f"Gemini analysis failed: {exc}")
            return self._fallback_insights(overall_score)

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    def _fallback_insights(self, overall_score: float) -> AIInsights:
        return AIInsights(
            summary=f"Website scored {overall_score}/100. Core metrics collected successfully.",
            strengths=["Performance, SEO, and content metrics analyzed"],
            weaknesses=["AI-generated insights unavailable"],
            quick_wins=["Review performance and SEO recommendations below"],
            strategic_recommendations=(
                "Enable Gemini AI by configuring GEMINI_API_KEY to receive "
                "advanced strategic insights and recommendations."
            ),
        )

    def _build_prompt(
        self,
        url: str,
        desktop: Optional[DeviceAnalysis],
        mobile: Optional[DeviceAnalysis],
        overall_score: float,
    ) -> str:
        sections: list[str] = []

        if desktop:
            sections.append(
                f"""
DESKTOP ANALYSIS:
- Performance Score: {desktop.performance.score}/100
- SEO Score: {desktop.seo.score}/100
- FCP: {desktop.performance.first_contentful_paint}s
- LCP: {desktop.performance.largest_contentful_paint}s
- Word Count: {desktop.content.word_count}
- H1 Tags: {len(desktop.seo.h1_tags)}
- Missing Alt Tags: {desktop.seo.image_alt_tags_missing}/{desktop.seo.total_images}
"""
            )

        if mobile:
            sections.append(
                f"""
MOBILE ANALYSIS:
- Performance Score: {mobile.performance.score}/100
- SEO Score: {mobile.seo.score}/100
- CLS: {mobile.performance.cumulative_layout_shift}
- Time to Interactive: {mobile.performance.time_to_interactive}s
"""
            )

        context = "\n".join(sections)

        return f"""
You are an expert website analyst.

Website: {url}
Overall Score: {overall_score}/100

{context}

Provide:
1. A 2–3 sentence executive summary
2. Top 3 strengths
3. Top 3 weaknesses
4. 3–5 quick wins
5. One-paragraph strategic recommendation

Respond ONLY as valid JSON with this structure:
{{
  "summary": "...",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "quick_wins": ["..."],
  "strategic_recommendations": "..."
}}
"""

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        if text.startswith("```"):
            text = text.split("```", 2)[1]
        return text.strip()
