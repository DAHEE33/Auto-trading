from __future__ import annotations

import re
from bs4 import BeautifulSoup


WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def summarize_html(html: str, max_chars: int = 500) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    paragraphs = [
        normalize_text(p.get_text(" ", strip=True))
        for p in soup.find_all("p")
    ]
    paragraphs = [p for p in paragraphs if len(p) >= 30]
    if not paragraphs:
        body_text = normalize_text(soup.get_text(" ", strip=True))
        return body_text[:max_chars]

    joined = " ".join(paragraphs[:3])
    return joined[:max_chars]

