"""
Content analysis utilities.
Pure, stateless functions including Flesch Reading Ease calculation.
"""

import re
from typing import Dict, List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.models.schemas import ContentAnalysis


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_content(html: str, base_url: str) -> ContentAnalysis:
    soup = BeautifulSoup(html, "html.parser")

    text = _extract_visible_text(soup)
    words = _tokenize_words(text)

    word_count = len(words)
    paragraph_count = len(soup.find_all("p"))

    readability = _flesch_reading_ease(text)
    heading_score = _heading_structure_score(soup)

    internal_links, external_links, broken_links = _analyze_links(soup, base_url)
    keyword_density = _keyword_density(words)
    content_gaps = _detect_content_gaps(word_count, soup)

    return ContentAnalysis(
        word_count=word_count,
        paragraph_count=paragraph_count,
        heading_structure_score=heading_score,
        readability_score=round(readability, 2),
        keyword_density=keyword_density,
        internal_links=internal_links,
        external_links=external_links,
        broken_links=broken_links,
        content_gaps=content_gaps,
    )


# ---------------------------------------------------------------------------
# Internals (pure helpers)
# ---------------------------------------------------------------------------

def _extract_visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    return " ".join(soup.stripped_strings)


def _tokenize_words(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


# ----------------------- Readability (Flesch) -------------------------------

def _flesch_reading_ease(text: str) -> float:
    sentences = max(1, len(re.findall(r"[.!?]", text)))
    words = _tokenize_words(text)
    syllables = sum(_count_syllables(word) for word in words)

    if not words:
        return 0.0

    words_count = len(words)

    # Flesch Reading Ease formula
    return 206.835 - 1.015 * (words_count / sentences) - 84.6 * (syllables / words_count)


def _count_syllables(word: str) -> int:
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_char_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_char_was_vowel:
            count += 1
        prev_char_was_vowel = is_vowel

    if word.endswith("e") and count > 1:
        count -= 1

    return max(count, 1)


# ----------------------- Structure & Links ----------------------------------

def _heading_structure_score(soup: BeautifulSoup) -> float:
    h1 = len(soup.find_all("h1"))
    h2 = len(soup.find_all("h2"))
    h3 = len(soup.find_all("h3"))

    score = 100
    if h1 == 0:
        score -= 30
    elif h1 > 1:
        score -= 10

    if h2 == 0:
        score -= 20

    if h3 == 0:
        score -= 10

    return max(score, 0)


def _analyze_links(soup: BeautifulSoup, base_url: str) -> tuple[int, int, int]:
    internal = 0
    external = 0
    broken = 0

    base_domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        href = a.get("href")
        if href.startswith("#"):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        if not parsed.scheme.startswith("http"):
            broken += 1
        elif parsed.netloc == base_domain:
            internal += 1
        else:
            external += 1

    return internal, external, broken


# ----------------------- Keywords & Gaps ------------------------------------

def _keyword_density(words: List[str], top_n: int = 10) -> Dict[str, float]:
    if not words:
        return {}

    freq: Dict[str, int] = {}
    for word in words:
        if len(word) <= 3:
            continue
        freq[word] = freq.get(word, 0) + 1

    total = len(words)
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]

    return {word: round(count / total, 4) for word, count in sorted_words}


def _detect_content_gaps(word_count: int, soup: BeautifulSoup) -> List[str]:
    gaps: List[str] = []

    if word_count < 300:
        gaps.append("Content length is low (<300 words)")

    if not soup.find("h2"):
        gaps.append("No H2 subheadings found")

    if not soup.find("ul") and not soup.find("ol"):
        gaps.append("No bullet or numbered lists found")

    return gaps
