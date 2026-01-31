"""
SEO analysis utilities.
Pure, stateless functions for extracting SEO signals from HTML content.
"""

from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.models.schemas import SEOAnalysis


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_seo(html: str, base_url: str) -> SEOAnalysis:
    soup = BeautifulSoup(html, "html.parser")

    title = _get_title(soup)
    meta_description = _get_meta_description(soup)
    h1_tags = _get_headings(soup, "h1")
    h2_tags = _get_headings(soup, "h2")
    canonical_url = _get_canonical_url(soup, base_url)
    meta_robots = _get_meta_robots(soup)
    open_graph_tags = _get_open_graph_tags(soup)
    structured_data = _has_structured_data(soup)

    total_images, missing_alt = _analyze_image_alt_tags(soup)

    score = _calculate_seo_score(
        title=title,
        meta_description=meta_description,
        h1_count=len(h1_tags),
        canonical_url=canonical_url,
        missing_alt=missing_alt,
        total_images=total_images,
    )

    return SEOAnalysis(
        score=score,
        title=title,
        title_length=len(title) if title else None,
        meta_description=meta_description,
        meta_description_length=len(meta_description) if meta_description else None,
        h1_tags=h1_tags,
        h2_tags=h2_tags,
        canonical_url=canonical_url,
        meta_robots=meta_robots,
        open_graph_tags=open_graph_tags,
        structured_data=structured_data,
        image_alt_tags_missing=missing_alt,
        total_images=total_images,
    )


# ---------------------------------------------------------------------------
# Internals (pure helpers)
# ---------------------------------------------------------------------------

def _get_title(soup: BeautifulSoup) -> str | None:
    tag = soup.title
    return tag.string.strip() if tag and tag.string else None


def _get_meta_description(soup: BeautifulSoup) -> str | None:
    tag = soup.find("meta", attrs={"name": "description"})
    return tag.get("content", "").strip() if tag else None


def _get_headings(soup: BeautifulSoup, tag_name: str) -> List[str]:
    return [tag.get_text(strip=True) for tag in soup.find_all(tag_name)]


def _get_canonical_url(soup: BeautifulSoup, base_url: str) -> str | None:
    tag = soup.find("link", rel="canonical")
    if tag and tag.get("href"):
        return urljoin(base_url, tag["href"])
    return None


def _get_meta_robots(soup: BeautifulSoup) -> str | None:
    tag = soup.find("meta", attrs={"name": "robots"})
    return tag.get("content") if tag else None


def _get_open_graph_tags(soup: BeautifulSoup) -> Dict[str, str]:
    og_tags: Dict[str, str] = {}
    for tag in soup.find_all("meta"):
        prop = tag.get("property")
        if prop and prop.startswith("og:"):
            og_tags[prop] = tag.get("content", "")
    return og_tags


def _has_structured_data(soup: BeautifulSoup) -> bool:
    return bool(soup.find("script", type="application/ld+json"))


def _analyze_image_alt_tags(soup: BeautifulSoup) -> tuple[int, int]:
    images = soup.find_all("img")
    total = len(images)
    missing = sum(1 for img in images if not img.get("alt"))
    return total, missing


def _calculate_seo_score(
    *,
    title: str | None,
    meta_description: str | None,
    h1_count: int,
    canonical_url: str | None,
    missing_alt: int,
    total_images: int,
) -> float:
    score = 100

    if not title:
        score -= 15
    elif len(title) < 30 or len(title) > 65:
        score -= 5

    if not meta_description:
        score -= 15
    elif len(meta_description) < 70 or len(meta_description) > 160:
        score -= 5

    if h1_count == 0:
        score -= 15
    elif h1_count > 1:
        score -= 5

    if not canonical_url:
        score -= 5

    if total_images > 0:
        missing_ratio = missing_alt / total_images
        if missing_ratio > 0.5:
            score -= 10
        elif missing_ratio > 0.2:
            score -= 5

    return max(score, 0)
