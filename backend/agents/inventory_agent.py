"""
Inventory Agent
---------------
Source: EIA Weekly Petroleum Status Report via the free EIA Open Data API
(https://www.eia.gov/opendata/register.php - instant free signup).

Pulls: crude stocks, refinery utilization %, US imports/exports.
"""
import os
import sys
import json
from datetime import datetime, timezone

import httpx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

log = get_logger("inventory_agent")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(DATA_DIR, "inventory_agent.json")

EIA_BASE = "https://api.eia.gov/v2"

# EIA series IDs (Weekly Petroleum Status Report) - verify/update at
# https://www.eia.gov/opendata/browser/petroleum/stoc/wstk if these change.
SERIES = {
    "crude_stocks_kbbl": "PET.WCESTUS1.W",         # Weekly US Ending Stocks of Crude Oil
    "refinery_utilization_pct": "PET.WPULEUS3.W",  # Weekly Refinery Utilization
    "crude_imports_kbbl_day": "PET.WCRIMUS2.W",    # Weekly US Crude Imports
    "crude_exports_kbbl_day": "PET.WCREXUS2.W",    # Weekly US Crude Exports
}


def fetch_series(series_id: str, api_key: str, length: int = 8) -> list[dict]:
    url = f"{EIA_BASE}/seriesid/{series_id}"
    params = {"api_key": api_key, "length": length, "sort[0][column]": "period", "sort[0][direction]": "desc"}
    try:
        resp = httpx.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("response", {}).get("data", [])
        log.debug(f"[RAW MATCH] series={series_id} rows={len(rows)}")
        return rows
    except Exception as e:
        log.error(f"[EIA] fetch failed for {series_id}: {e}")
        return []


def run_once() -> dict:
    log.info("Inventory Agent: starting fetch cycle")
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        log.warning("EIA_API_KEY not set - writing empty/placeholder output")
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "EIA_API_KEY not set",
            "metrics": {},
        }
        with open(OUTPUT_PATH, "w") as f:
            json.dump(output, f, indent=2)
        return output

    metrics = {}
    for name, series_id in SERIES.items():
        rows = fetch_series(series_id, api_key)
        if rows:
            latest = rows[0]
            metrics[name] = {
                "value": latest.get("value"),
                "period": latest.get("period"),
            }
            log.info(f"Inventory Agent: {name} = {latest.get('value')} ({latest.get('period')})")
        else:
            metrics[name] = None

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    log.info(f"Inventory Agent: wrote metrics -> {OUTPUT_PATH}")
    return output


if __name__ == "__main__":
    run_once()
