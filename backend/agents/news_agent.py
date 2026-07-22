"""
News Agent
----------
Sources: GDELT (free, no key) + NewsAPI (free tier, 100 req/day).
Reuters has no free API, so if you want Reuters specifically you'll need to
add a Playwright scrape block (respect robots.txt / their T&Cs) — left as a
clearly marked TODO below rather than shipped by default.

Output JSON (written to data/news_agent.json):
{
  "timestamp": "...",
  "articles": [
     {"title", "source", "url", "published", "corridor", "sentiment_score",
      "disruption_keywords": [...] }
  ],
  "aggregate": {"disruption_probability_by_corridor": {"hormuz": 0.62, ...}}
}
"""
import os
import sys
import json
import time
from datetime import datetime, timezone

import httpx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger
from rag.vector_store import add_news

log = get_logger("news_agent")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(DATA_DIR, "news_agent.json")

CORRIDORS = {
    "hormuz": ["strait of hormuz", "iran", "persian gulf", "gulf of oman"],
    "red_sea": ["red sea", "houthi", "bab el-mandeb", "suez"],
    "opec": ["opec", "opec+", "saudi arabia", "production cut"],
    "russia": ["russia", "urals crude", "sanctions on russia"],
}

DISRUPTION_KEYWORDS = [
    "attack", "strike", "sanction", "blockade", "seize", "seizure",
    "closure", "disrupt", "tanker", "missile", "war", "escalation",
    "embargo", "shortage",
]

NEGATIVE_WORDS = ["attack", "war", "sanction", "blockade", "seize", "crisis",
                   "disrupt", "conflict", "strike", "embargo", "shortage"]
POSITIVE_WORDS = ["deal", "agreement", "ceasefire", "resolve", "stabilize",
                   "truce", "restore", "ease"]


def tag_corridor(text: str) -> str:
    text_l = text.lower()
    for corridor, keywords in CORRIDORS.items():
        if any(kw in text_l for kw in keywords):
            return corridor
    return "general"


def simple_sentiment(text: str) -> float:
    """Cheap lexicon-based sentiment in [-1, 1]. Good enough for a live
    dashboard signal; swap for a proper FinBERT-style model if you have time."""
    text_l = text.lower()
    neg = sum(text_l.count(w) for w in NEGATIVE_WORDS)
    pos = sum(text_l.count(w) for w in POSITIVE_WORDS)
    total = neg + pos
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 2)


def extract_disruption_keywords(text: str) -> list[str]:
    text_l = text.lower()
    return [kw for kw in DISRUPTION_KEYWORDS if kw in text_l]


def fetch_gdelt(query: str = "oil OR crude OR opec OR hormuz", max_records: int = 50) -> list[dict]:
    """GDELT DOC 2.0 API - free, no key required."""
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": max_records,
        "format": "json",
        "sort": "hybridrel",
    }
    try:
        resp = httpx.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])
        log.info(f"[GDELT] Fetched {len(articles)} articles")
        return [
            {
                "title": a.get("title", ""),
                "source": a.get("domain", "gdelt"),
                "url": a.get("url", ""),
                "published": a.get("seendate", ""),
            }
            for a in articles
        ]
    except Exception as e:
        log.error(f"[GDELT] fetch failed: {e}")
        return []


def fetch_newsapi(query: str = "crude oil OR Strait of Hormuz OR OPEC") -> list[dict]:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        log.warning("[NewsAPI] NEWSAPI_KEY not set, skipping")
        return []
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "language": "en", "sortBy": "publishedAt", "pageSize": 30}
    try:
        resp = httpx.get(url, params=params, headers={"X-Api-Key": api_key}, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])
        log.info(f"[NewsAPI] Fetched {len(articles)} articles")
        return [
            {
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", "newsapi"),
                "url": a.get("url", ""),
                "published": a.get("publishedAt", ""),
                "description": a.get("description", ""),
            }
            for a in articles
        ]
    except Exception as e:
        log.error(f"[NewsAPI] fetch failed: {e}")
        return []


# TODO (optional): Reuters has no free API. If you want it specifically,
# add a Playwright scrape here following the same pattern as
# agents/india_trade_agent.py (navigate -> wait_for_selector -> extract text
# -> log [RAW MATCH] lines while you tune selectors).


def run_once() -> dict:
    log.info("News Agent: starting fetch cycle")
    raw_articles = fetch_gdelt() + fetch_newsapi()

    processed = []
    corridor_scores: dict[str, list[float]] = {}

    for art in raw_articles:
        text = f"{art.get('title', '')}. {art.get('description', '')}"
        corridor = tag_corridor(text)
        sentiment = simple_sentiment(text)
        keywords = extract_disruption_keywords(text)

        log.debug(f"[RAW MATCH] title='{art.get('title', '')[:60]}' "
                  f"corridor={corridor} sentiment={sentiment} keywords={keywords}")

        processed.append({
            **art,
            "corridor": corridor,
            "sentiment_score": sentiment,
            "disruption_keywords": keywords,
        })

        # Index into RAG store so Recommendation Agent can retrieve it later
        if text.strip():
            add_news(text, {
                "date": art.get("published", datetime.now(timezone.utc).isoformat()),
                "corridor": corridor,
                "source": art.get("source", "unknown"),
                "sentiment": "negative" if sentiment < -0.2 else (
                    "positive" if sentiment > 0.2 else "neutral"),
            })

        corridor_scores.setdefault(corridor, []).append(
            1.0 if keywords else max(0.0, -sentiment)
        )

    disruption_probability = {
        corridor: round(sum(scores) / len(scores), 2)
        for corridor, scores in corridor_scores.items()
    }

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "articles": processed,
        "aggregate": {"disruption_probability_by_corridor": disruption_probability},
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    log.info(f"News Agent: wrote {len(processed)} articles -> {OUTPUT_PATH}")
    log.info(f"News Agent: corridor risk = {disruption_probability}")
    return output


if __name__ == "__main__":
    run_once()
