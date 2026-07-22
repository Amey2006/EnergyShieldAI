"""
India Trade Agent
-----------------
Sources: PPAC (ppac.gov.in), Ministry of Commerce trade stats, RBI.
None publish a free structured API for these specific tables, so this uses
Playwright to render the page and BeautifulSoup to pull row labels + values.

This follows the debugging pattern already established for PPAC scraping:
  1. Run with LOG_LEVEL=DEBUG.
  2. Read the [RAW MATCH] lines to see every row label actually found on
     the live page.
  3. Update ROW_KEYWORDS below to match the real labels (PPAC changes
     wording/table structure between releases).
  4. Re-run until the metrics you need come through clean.
"""
import os
import sys
import json
import re
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

log = get_logger("india_trade_agent")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(DATA_DIR, "india_trade_agent.json")

PPAC_URL = "https://ppac.gov.in/prices/international-crude-oil-price"
# Swap/add more PPAC report pages as needed, e.g. import/export snapshot,
# refinery-wise throughput, product-wise exports.

# Row-label keywords to look for in scraped tables. Update after checking
# [RAW MATCH] output against the live page's actual wording.
ROW_KEYWORDS = {
    "crude_import_mix": ["crude oil import", "import of crude"],
    "refinery_throughput": ["refinery throughput", "crude processed", "crude processing"],
    "product_exports": ["export of petroleum product", "poL export", "product export"],
    "import_bill": ["import bill", "value of crude oil import"],
}

NUMBER_RE = re.compile(r"[\d,]+\.?\d*")


def scrape_page(url: str, timeout_ms: int = 30000) -> str:
    log.info(f"Launching Playwright for {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=timeout_ms, wait_until="networkidle")
            page.wait_for_timeout(2000)  # let any lazy JS tables render
            html = page.content()
        except Exception as e:
            log.error(f"[Playwright] navigation failed: {e}")
            html = ""
        finally:
            browser.close()
    return html


def extract_rows(html: str) -> list[dict]:
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.find_all("tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    log.info(f"Extracted {len(rows)} raw table rows")
    return rows


def match_metrics(rows: list[list[str]]) -> dict:
    metrics = {}
    for row in rows:
        if not row:
            continue
        label = row[0].lower()
        log.debug(f"[RAW MATCH] row_label='{row[0]}' row={row}")
        for metric_name, keywords in ROW_KEYWORDS.items():
            if any(kw in label for kw in keywords):
                numbers = NUMBER_RE.findall(" ".join(row[1:]))
                metrics[metric_name] = {
                    "raw_row": row,
                    "numbers": numbers,
                }
                log.info(f"[MATCHED] {metric_name} <- '{row[0]}' -> {numbers}")
    return metrics


def run_once() -> dict:
    log.info("India Trade Agent: starting fetch cycle")
    html = scrape_page(PPAC_URL)
    rows = extract_rows(html)
    metrics = match_metrics(rows)

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": PPAC_URL,
        "metrics": metrics,
        "rows_scanned": len(rows),
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    log.info(f"India Trade Agent: matched {len(metrics)}/{len(ROW_KEYWORDS)} metrics -> {OUTPUT_PATH}")
    if len(metrics) < len(ROW_KEYWORDS):
        log.warning("Some metrics unmatched - check [RAW MATCH] debug logs and "
                    "update ROW_KEYWORDS to the page's current wording.")
    return output


if __name__ == "__main__":
    run_once()
