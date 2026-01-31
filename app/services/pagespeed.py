"""
PageSpeed performance analysis service.
Uses Google PageSpeed Insights API when available,
falls back to simulated metrics when API key is missing or API fails.
"""

import asyncio
import httpx
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import PerformanceMetrics, DeviceType

logger = get_logger(__name__)
settings = get_settings()


class PageSpeedService:
    def __init__(self) -> None:
        self.api_key = settings.pagespeed_api_key
        self.timeout = httpx.Timeout(settings.request_timeout)

        if not self.api_key:
            logger.warning("PAGESPEED_API_KEY not configured. Using simulated performance metrics.")

    async def analyze(self, url: str, device_type: DeviceType) -> PerformanceMetrics:
        """
        Analyze website performance for the given device.
        Uses real PageSpeed API when possible, otherwise simulated metrics.
        """

        if self.api_key:
            try:
                return await self._analyze_with_pagespeed(url, device_type)
            except Exception as exc:
                logger.error(f"PageSpeed API failed, falling back to simulation: {exc}")

        return await self._analyze_simulated(url, device_type)

    # ------------------------------------------------------------------
    # Real PageSpeed API
    # ------------------------------------------------------------------

    async def _analyze_with_pagespeed(self, url: str, device_type: DeviceType) -> PerformanceMetrics:
        strategy = "mobile" if device_type == DeviceType.MOBILE else "desktop"

        pagespeed_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "key": self.api_key,
            "strategy": strategy,
            "category": ["performance"],
        }

        logger.info(f"Calling PageSpeed API for {url} ({strategy})")

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.get(pagespeed_url, params=params)
            response.raise_for_status()
            data = response.json()

        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        performance_score = categories.get("performance", {}).get("score", 0) * 100

        fcp = audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000
        lcp = audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000
        tti = audits.get("interactive", {}).get("numericValue", 0) / 1000
        tbt = audits.get("total-blocking-time", {}).get("numericValue", 0)
        cls = audits.get("cumulative-layout-shift", {}).get("numericValue", 0)
        speed_index = audits.get("speed-index", {}).get("numericValue", 0) / 1000

        logger.info(
            f"PageSpeed results ({strategy}): score={performance_score:.1f}, "
            f"LCP={lcp:.2f}s, FCP={fcp:.2f}s"
        )

        return PerformanceMetrics(
            score=round(performance_score, 1),
            first_contentful_paint=round(fcp, 2),
            speed_index=round(speed_index, 2),
            largest_contentful_paint=round(lcp, 2),
            time_to_interactive=round(tti, 2),
            total_blocking_time=round(tbt, 0),
            cumulative_layout_shift=round(cls, 3),
        )

    # ------------------------------------------------------------------
    # Simulated fallback
    # ------------------------------------------------------------------

    async def _analyze_simulated(self, url: str, device_type: DeviceType) -> PerformanceMetrics:
        start_time = asyncio.get_event_loop().time()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await client.get(url)

            load_time = asyncio.get_event_loop().time() - start_time

            if load_time < 1.0:
                score = 95
            elif load_time < 2.0:
                score = 85
            elif load_time < 3.0:
                score = 70
            elif load_time < 5.0:
                score = 50
            else:
                score = 30

            logger.info(
                f"Simulated performance ({device_type.value}): "
                f"score={score}, load_time={load_time:.2f}s"
            )

            return PerformanceMetrics(
                score=round(score, 1),
                first_contentful_paint=round(load_time * 0.3, 2),
                speed_index=round(load_time * 0.5, 2),
                largest_contentful_paint=round(load_time * 0.7, 2),
                time_to_interactive=round(load_time * 0.9, 2),
                total_blocking_time=round(max(0, load_time - 2) * 100, 0),
                cumulative_layout_shift=0.08 if device_type == DeviceType.MOBILE else 0.03,
            )

        except Exception as exc:
            logger.error(f"Simulated performance failed: {exc}")
            return PerformanceMetrics(score=0)
