"""
FastAPI backend. Purely reads whatever JSON the agents have last written to
data/*.json and serves it to the React dashboard. Also exposes a
/api/analyze-news endpoint for the "paste a news paragraph" test box.
"""
import os
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.logger import get_logger
from agents.news_agent import tag_corridor, simple_sentiment, extract_disruption_keywords
from rag.vector_store import add_news, query as rag_query

log = get_logger("api")

app = FastAPI(title="Energy Supply Chain Resilience API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this for anything beyond a hackathon demo
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def read_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {"error": f"{filename} not generated yet - start orchestrator.py"}
    with open(path) as f:
        return json.load(f)


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/news")
def get_news():
    return read_json("news_agent.json")


@app.get("/api/market-intelligence")
def get_market_intel():
    return read_json("market_intelligence_agent.json")


@app.get("/api/inventory")
def get_inventory():
    return read_json("inventory_agent.json")


@app.get("/api/india-trade")
def get_india_trade():
    return read_json("india_trade_agent.json")


@app.get("/api/shipping")
def get_shipping():
    return read_json("shipping_agent.json")


@app.get("/api/prediction")
def get_prediction():
    return read_json("prediction_agent.json")


@app.get("/api/recommendation")
def get_recommendation():
    return read_json("recommendation_agent.json")


@app.get("/api/dashboard")
def get_dashboard():
    """Single aggregate endpoint - the frontend polls this every 60s."""
    return {
        "news": read_json("news_agent.json"),
        "market_intelligence": read_json("market_intelligence_agent.json"),
        "inventory": read_json("inventory_agent.json"),
        "india_trade": read_json("india_trade_agent.json"),
        "shipping": read_json("shipping_agent.json"),
        "prediction": read_json("prediction_agent.json"),
        "recommendation": read_json("recommendation_agent.json"),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


class NewsTestInput(BaseModel):
    text: str


@app.post("/api/analyze-news")
def analyze_news(payload: NewsTestInput):
    """Powers the 'paste a news paragraph' test box in the UI. Runs the same
    tagging logic as the live News Agent, and indexes it into RAG tagged as
    a manual test so it doesn't get confused with live-scraped articles."""
    text = payload.text
    corridor = tag_corridor(text)
    sentiment = simple_sentiment(text)
    keywords = extract_disruption_keywords(text)

    add_news(text, {
        "date": datetime.now(timezone.utc).isoformat(),
        "corridor": corridor,
        "source": "manual_test_input",
        "sentiment": "negative" if sentiment < -0.2 else (
            "positive" if sentiment > 0.2 else "neutral"),
    })

    related = rag_query(text, k=3, corridor=corridor)

    log.info(f"[Manual test] corridor={corridor} sentiment={sentiment} keywords={keywords}")

    return {
        "corridor": corridor,
        "sentiment_score": sentiment,
        "disruption_keywords": keywords,
        "related_existing_context": related,
    }
