import json
import re
from typing import Optional

from app.core.logging import get_logger
from app.core.deepseek_client import get_client, DEEPSEEK_API_URL
from app.models.schemas import DeviceAnalysis, AIInsights

logger = get_logger(__name__)


class GeminiAnalyzer:
    """
    Legacy name kept intentionally.
    Backend = DeepSeek
    """

    def __init__(self) -> None:
        self.model = "deepseek-chat"
        logger.info("🧠 GeminiAnalyzer (DeepSeek backend) initialized")

    def _extract_json(self, text: str) -> dict:
        """
        Extract first valid JSON object from LLM output.
        Handles markdown, prose, and formatting noise.
        """
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in AI response")

        return json.loads(match.group())

    async def generate_insights(
        self,
        url: str,
        desktop: Optional[DeviceAnalysis],
        mobile: Optional[DeviceAnalysis],
        overall_score: float,
    ) -> AIInsights:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior website performance and SEO consultant. "
                        "Return ONLY valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(url, overall_score),
                },
            ],
            "temperature": 0.3,
        }

        try:
            client = await get_client()
            async with client:
                response = await client.post(DEEPSEEK_API_URL, json=payload)
                response.raise_for_status()

                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()

                parsed = self._extract_json(content)
                return AIInsights(**parsed)

        except Exception:
            logger.error("❌ AI failed", exc_info=True)
            return self._fallback(overall_score)

    def _fallback(self, score: float) -> AIInsights:
        return AIInsights(
            summary=f"Website scored {score}/100. AI unavailable.",
            strengths=["Performance data collected"],
            weaknesses=["AI analysis failed"],
            quick_wins=["Review performance metrics"],
            strategic_recommendations="Check AI configuration.",
        )

    def _build_prompt(self, url: str, score: float) -> str:
        return f"""
Website URL: {url}
Overall Score: {score}/100

Return ONLY valid JSON in this format:

{{
  "summary": "...",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "quick_wins": ["..."],
  "strategic_recommendations": "..."
}}
"""
