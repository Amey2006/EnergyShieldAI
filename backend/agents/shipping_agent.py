"""
Shipping Agent
--------------
Sources: AIS vessel position data + freight indices.

Free AIS options change frequently and most meaningful ones are paid
(MarineTraffic, Spire). AISHub (https://www.aishub.net) offers free access
if you contribute your own AIS receiver feed, which isn't realistic for a
hackathon. The practical free path is:
  1. AISStream.io - free websocket AIS feed with a free API key
     (https://aisstream.io) - used below.
  2. If that's unavailable, this agent falls back to a small set of
     illustrative tanker positions along known India-bound corridors so the
     map/dashboard still has something to render during a demo.

Freight indices (Baltic Dirty Tanker Index etc.) are paywalled; as a free
proxy this scrapes a public freight-index summary page for headline moves.
"""
import os
import sys
import json
import random
from datetime import datetime, timezone

import httpx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

log = get_logger("shipping_agent")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(DATA_DIR, "shipping_agent.json")

# Known chokepoint coordinates for map plotting even when live AIS is down.
CHOKEPOINTS = {
    "strait_of_hormuz": {"lat": 26.5667, "lon": 56.25},
    "bab_el_mandeb": {"lat": 12.5833, "lon": 43.3333},
    "suez_canal": {"lat": 30.5852, "lon": 32.2654},
}

FALLBACK_VESSELS = [
    {"vessel_id": "IMO9234567", "name": "SAMPLE VLCC 1", "route": "hormuz_to_india",
     "lat": 25.9, "lon": 57.1, "delay_days": 1.2},
    {"vessel_id": "IMO9345678", "name": "SAMPLE VLCC 2", "route": "hormuz_to_india",
     "lat": 21.4, "lon": 63.2, "delay_days": 0.4},
    {"vessel_id": "IMO9456789", "name": "SAMPLE SUEZMAX", "route": "red_sea_to_india",
     "lat": 13.9, "lon": 47.5, "delay_days": 2.8},
]


def fetch_ais_stream(api_key: str) -> list[dict]:
    """AISStream.io free websocket feed. A full websocket client is more
    setup than fits a single polling agent cleanly - if you wire this up,
    keep a small background websocket listener populating a buffer that
    this function reads from. Left as a stub returning [] until you do."""
    log.warning("[AIS] Live websocket integration not wired up yet - see "
                "aisstream.io docs to add a background listener.")
    return []


def fetch_freight_index_proxy() -> dict:
    """Scrapes a public freight index summary as a free proxy for Baltic
    Dirty Tanker Index moves. Swap the URL/selectors for whatever free
    summary page you find reliable."""
    url = "https://www.balticexchange.com/en/data-services/market-information0/dirty-tanker.html"
    try:
        resp = httpx.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        log.info("[Freight] Fetched Baltic Exchange summary page")
        return {"source": url, "raw_length": len(resp.text)}
    except Exception as e:
        log.error(f"[Freight] fetch failed: {e}")
        return {"source": url, "error": str(e)}


def run_once() -> dict:
    log.info("Shipping Agent: starting fetch cycle")
    api_key = os.getenv("AISSTREAM_API_KEY")

    vessels = fetch_ais_stream(api_key) if api_key else []
    if not vessels:
        log.info("Shipping Agent: using illustrative fallback vessel positions for demo continuity")
        vessels = FALLBACK_VESSELS

    congestion_index = round(random.uniform(0.2, 0.8), 2)  # placeholder until real AIS density calc
    freight = fetch_freight_index_proxy()

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chokepoints": CHOKEPOINTS,
        "vessels": vessels,
        "congestion_index": congestion_index,
        "freight_index_proxy": freight,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    log.info(f"Shipping Agent: wrote {len(vessels)} vessel records -> {OUTPUT_PATH}")
    return output


if __name__ == "__main__":
    run_once()
