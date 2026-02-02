import json
from typing import Optional

from fastapi.concurrency import run_in_threadpool

from app.core.logging import get_logger
from app.core.deepseek_client import get_deepseek_client, DEEPSEEK_API_URL
from app.models.schemas import DeviceAnalysis, AIInsights

logger = get_logger(__name__)


class DeepSeekAnalyzer:
    def __init__(self) -> None:
        self.model = "deepseek-chat"
        logger.info("🧠 DeepSeek Analyzer initialized")

    async def generate_insights(
        self,
        url: str,
        desktop: Optional[DeviceAnalysis],
        mobile: Optional[DeviceAnalysis],
        overall_score: float,
    ) -> AIInsights:
        prompt = self._build_prompt(url, desktop, mobile, overall_score)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior website performance and SEO consultant. "
                        "You MUST respond with valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.3,
        }

        try:
            async with get_deepseek_client() as client:
                logger.info("📤 Sending request to DeepSeek")

                response = await client.post(DEEPSEEK_API_URL, json=payload)
                response.raise_for_status()

                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()

                logger.info("📥 DeepSeek response received")

                parsed = json.loads(content)
                return AIInsights(**parsed)

        except Exception as exc:
            logger.error(f"❌ DeepSeek failed: {exc}", exc_info=True)
            return self._fallback_insights(overall_score)

    # -------------------------------------------------

    def _fallback_insights(self, overall_score: float) -> AIInsights:
        return AIInsights(
            summary=f"Website scored {overall_score}/100. AI unavailable.",
            strengths=["Performance data collected"],
            weaknesses=["AI analysis failed"],
            quick_wins=["Review performance metrics"],
            strategic_recommendations="Check AI service configuration.",
        )

    def _build_prompt(
        self,
        url: str,
        desktop: Optional[DeviceAnalysis],
        mobile: Optional[DeviceAnalysis],
        overall_score: float,
    ) -> str:
        return f"""
Website URL: {url}
Overall Score: {overall_score}/100

Respond ONLY with valid JSON in the following format:

{{
  "summary": "High-level assessment of the website",
  "strengths": ["List strengths"],
  "weaknesses": ["List weaknesses"],
  "quick_wins": ["Immediate improvements"],
  "strategic_recommendations": "Long-term strategy"
}}

Do not include markdown.
Do not include explanations.
Do not include code fences.
"""
