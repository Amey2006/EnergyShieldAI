"""
Market Intelligence Agent
-------------------------
Sources: IEA Oil Market Report, OPEC Monthly Oil Market Report, EIA STEO.
None of these publish a clean free JSON API - they publish monthly PDF/HTML
reports. This agent downloads the report page, extracts text, and pulls out
headline numbers with regex/keyword matching (same iterative pattern as the
India Trade Agent: log [RAW MATCH] lines, refine the keyword list against
real report wording).

Because report layouts vary release to release, treat the regexes below as
a starting point, not a finished parser - run once, check the [RAW MATCH]
logs, then tighten patterns against the actual current report text.
"""
import os
import sys
import re
import json
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

log = get_logger("market_intelligence_agent")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(DATA_DIR, "market_intelligence_agent.json")

# EIA STEO has a machine-readable summary page - most reliable of the three.
EIA_STEO_URL = "https://www.eia.gov/outlooks/steo/"
# IEA and OPEC reports are PDF-gated / paywalled for full detail; their
# public summary/press-release pages are the practical free source.
IEA_SUMMARY_URL = "https://www.iea.org/reports/oil-market-report-latest-release"
OPEC_SUMMARY_URL = "https://www.opec.org/opec_web/en/publications/338.htm"

NUMBER_RE = re.compile(r"(-?\d+\.?\d*)\s*(mb/d|million barrels|mb|%)", re.IGNORECASE)

KEYWORDS = [
    "demand growth", "supply growth", "inventory", "stock draw", "stock build",
    "forecast revision", "production", "opec+", "non-opec",
]


def fetch_page_text(url: str) -> str:
    try:
        resp = httpx.get(url, timeout=20, follow_redirects=True,
                          headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text
    except Exception as e:
        log.error(f"[fetch] failed for {url}: {e}")
        return ""


def extract_snippets(text: str, keywords: list[str], window: int = 120) -> list[dict]:
    snippets = []
    text_l = text.lower()
    for kw in keywords:
        idx = text_l.find(kw)
        if idx == -1:
            continue
        start = max(0, idx - window // 2)
        end = min(len(text), idx + window)
        snippet = text[start:end]
        numbers = NUMBER_RE.findall(snippet)
        log.debug(f"[RAW MATCH] keyword='{kw}' snippet='{snippet[:100]}...' numbers={numbers}")
        snippets.append({"keyword": kw, "snippet": snippet, "numbers": numbers})
    return snippets


def run_once() -> dict:
    log.info("Market Intelligence Agent: starting fetch cycle")

    sources = {
        "eia_steo": EIA_STEO_URL,
        "iea": IEA_SUMMARY_URL,
        "opec": OPEC_SUMMARY_URL,
    }

    report = {}
    for name, url in sources.items():
        text = fetch_page_text(url)
        snippets = extract_snippets(text, KEYWORDS) if text else []
        report[name] = {
            "url": url,
            "fetched_chars": len(text),
            "snippets": snippets,
        }
        log.info(f"Market Intelligence Agent: {name} -> {len(snippets)} keyword snippets")

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report": report,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    log.info(f"Market Intelligence Agent: wrote -> {OUTPUT_PATH}")
    return output


if __name__ == "__main__":
    run_once()
