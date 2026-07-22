"""
Recommendation Agent
---------------------
The only agent that calls the LLM. It combines:
  - Prediction Agent's statistical forecast (numbers come from ARIMA/GARCH,
    NOT the LLM)
  - Corridor disruption probabilities from the News Agent
  - Inventory/shipping metrics
  - Relevant retrieved news context from the RAG store

...and asks the LLM only to prioritize, explain, and suggest concrete
rerouting actions in natural language - grounded in the retrieved snippets,
which are shown back to the user for traceability.
"""
import os
import sys
import json
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger
from utils.llm_client import chat_json
from rag.vector_store import query as rag_query

log = get_logger("recommendation_agent")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "recommendation_agent.json")

AGENT_FILES = {
    "prediction": "prediction_agent.json",
    "news": "news_agent.json",
    "inventory": "inventory_agent.json",
    "india_trade": "india_trade_agent.json",
    "shipping": "shipping_agent.json",
}

SYSTEM_PROMPT = """You are the Recommendation Agent in an energy supply chain
resilience system for India's crude oil imports. You are given:
- A statistical price/volatility forecast (already computed - do not
  recompute or contradict the numbers).
- Corridor disruption probabilities.
- Inventory and shipping metrics.
- Retrieved news snippets relevant to the highest-risk corridor.

Your job: produce a JSON recommendation with:
{
  "risk_level": "low" | "moderate" | "high" | "critical",
  "primary_corridor_of_concern": "...",
  "summary": "2-3 sentence plain-English situation summary",
  "recommended_actions": [
     {"action": "...", "rationale": "...", "urgency": "immediate"|"this_week"|"monitor"}
  ],
  "alternative_procurement_routes": ["..."],
  "cited_news_snippet_indices": [0, 2]
}
Ground every claim in the data given to you. Do not invent numbers. If data
is missing, say so rather than guessing.
"""


def load_json(name: str) -> dict:
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def build_context() -> dict:
    context = {key: load_json(fname) for key, fname in AGENT_FILES.items()}
    return context


def top_risk_corridor(context: dict) -> str:
    probs = context.get("prediction", {}).get("corridor_disruption_probability", {})
    if not probs:
        return "hormuz"  # sensible default given India's exposure
    return max(probs, key=probs.get)


def run_once() -> dict:
    log.info("Recommendation Agent: starting cycle")
    context = build_context()
    corridor = top_risk_corridor(context)

    retrieved = rag_query(
        f"disruption risk news for {corridor} corridor affecting crude oil supply",
        k=5,
        corridor=corridor,
    )
    log.info(f"Recommendation Agent: retrieved {len(retrieved)} RAG snippets for corridor={corridor}")

    user_prompt = json.dumps({
        "primary_corridor": corridor,
        "prediction": context.get("prediction", {}),
        "inventory": context.get("inventory", {}),
        "india_trade": context.get("india_trade", {}),
        "shipping": context.get("shipping", {}),
        "retrieved_news_snippets": [r["text"][:400] for r in retrieved],
    }, default=str)

    llm_output = chat_json(SYSTEM_PROMPT, user_prompt)

    if "error" in llm_output:
        log.error(f"Recommendation Agent: LLM call failed, writing fallback output")
        llm_output = {
            "risk_level": "unknown",
            "primary_corridor_of_concern": corridor,
            "summary": "LLM call failed - see error field. Statistical forecast "
                       "below is still valid and computed independently.",
            "recommended_actions": [],
            "alternative_procurement_routes": [],
            "error": llm_output.get("error"),
        }

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "primary_corridor": corridor,
        "statistical_forecast": context.get("prediction", {}),
        "retrieved_context": retrieved,
        "recommendation": llm_output,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    log.info(f"Recommendation Agent: wrote recommendation (risk_level="
              f"{llm_output.get('risk_level')}) -> {OUTPUT_PATH}")
    return output


if __name__ == "__main__":
    run_once()
