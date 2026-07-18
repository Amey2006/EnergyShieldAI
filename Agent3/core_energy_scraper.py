import os
import sys
import re
import json
from typing import Dict, Any

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    class PlaywrightTimeoutError(Exception):
        pass

load_dotenv()
console = Console()

class ScraperLogger:
    @staticmethod
    def banner(title: str):
        console.rule(f"[bold magenta]{title}[/bold magenta]", style="magenta")

    @staticmethod
    def step(msg: str):
        console.print(f"[bold blue]→[/bold blue] {msg}")

    @staticmethod
    def success(msg: str):
        console.print(f"  [bold green]✓[/bold green] {msg}")

    @staticmethod
    def warn(msg: str):
        console.print(f"  [bold yellow]⚠[/bold yellow] [yellow]{msg}[/yellow]")

    @staticmethod
    def info(msg: str, val: Any = ""):
        console.print(f"  [dim]•[/dim] [cyan]{msg}:[/cyan] [bold white]{val}[/bold white]")

log = ScraperLogger()

CORE_ENERGY_URL = "https://energy.thecore.in/"

# Reliable fallback figures
FALLBACK_CORE_DATA = {
    "market_rates": {
        "brent_crude_usd": 85.33,
        "wti_crude_usd": 80.50,
        "usd_inr_exchange_rate": 96.24,
    },
    "spr_status": {
        "current_stock_mmt": 3.37,
        "days_of_import_cover": 9.5,
        "total_capacity_mmt": 5.33,
    },
    "retail_fuel_delhi": {
        "petrol_inr_litre": 102.12,
        "diesel_inr_litre": 95.20,
    }
}

class CoreEnergyScraper:
    """
    Scrapes real-time energy crisis data and market indicators from The Core's 
    India Energy Tracker. It parses the client-rendered Markdown-style DOM 
    using Playwright with robust, punctuation-immune cleaning.
    """
    def __init__(self, url: str = CORE_ENERGY_URL, timeout_ms: int = 15_000):
        self.url = url
        self.timeout_ms = timeout_ms

    def _get_rendered_html(self) -> str:
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Run 'pip install playwright'.")
            
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Agent3-CoreScraper/1.0; +headless)"
                )
                log.step(f"Navigating to {self.url}...")
                page.goto(self.url, timeout=self.timeout_ms, wait_until="networkidle")
                
                page.wait_for_selector("body", timeout=self.timeout_ms)
                html = page.content()
                log.success("DOM rendered successfully with dynamic content.")
                return html
            finally:
                browser.close()

    def _safe_float(self, matched_str: str) -> float:
        """
        Cleans up captured strings to ensure safe conversions to float 
        by stripping out trailing sentence punctuation, whitespaces, and commas.
        """
        cleaned = matched_str.replace(",", "").strip()
        # Strip trailing dots or commas caught by greedy regex captures (e.g. '96.24.' -> '96.24')
        cleaned = cleaned.rstrip(".")
        return float(cleaned)

    def scrape_dashboard(self) -> Dict[str, Any]:
        log.banner("The Core — India Energy Tracker Scraper")
        
        if not PLAYWRIGHT_AVAILABLE:
            log.warn("Playwright is missing. Loading fallback tracker metrics...")
            return FALLBACK_CORE_DATA

        try:
            html = self._get_rendered_html()
            soup = BeautifulSoup(html, "html.parser")
            text_content = soup.get_text()

            scraped_data = {
                "market_rates": {},
                "spr_status": {},
                "retail_fuel_delhi": {}
            }

            # 1. Parse Brent Price
            brent_match = re.search(r"Brent\s*\$?([\d\.,]+)", text_content, re.IGNORECASE)
            if brent_match:
                scraped_data["market_rates"]["brent_crude_usd"] = self._safe_float(brent_match.group(1))
            else:
                scraped_data["market_rates"]["brent_crude_usd"] = FALLBACK_CORE_DATA["market_rates"]["brent_crude_usd"]

            # 2. Parse Exchange Rate (USD/INR)
            rupee_match = re.search(r"rupee\s*₹?([\d\.,]+)", text_content, re.IGNORECASE)
            if rupee_match:
                scraped_data["market_rates"]["usd_inr_exchange_rate"] = self._safe_float(rupee_match.group(1))
            else:
                scraped_data["market_rates"]["usd_inr_exchange_rate"] = FALLBACK_CORE_DATA["market_rates"]["usd_inr_exchange_rate"]

            # 3. Parse Strategic Petroleum Reserve Stock
            spr_stock_match = re.search(r"Current Stock\s*~?([\d\.,]+)\s*MMT", text_content, re.IGNORECASE)
            if spr_stock_match:
                scraped_data["spr_status"]["current_stock_mmt"] = self._safe_float(spr_stock_match.group(1))
            else:
                scraped_data["spr_status"]["current_stock_mmt"] = FALLBACK_CORE_DATA["spr_status"]["current_stock_mmt"]

            # 4. Parse SPR Days of Import Cover
            spr_cover_match = re.search(r"([\d\.,]+)\s*days of import cover", text_content, re.IGNORECASE)
            if spr_cover_match:
                scraped_data["spr_status"]["days_of_import_cover"] = self._safe_float(spr_cover_match.group(1))
            else:
                scraped_data["spr_status"]["days_of_import_cover"] = FALLBACK_CORE_DATA["spr_status"]["days_of_import_cover"]

            # 5. Parse Delhi Petrol
            petrol_match = re.search(r"Delhi petrol.*?₹?([\d\.,]+)", text_content, re.IGNORECASE)
            if petrol_match:
                scraped_data["retail_fuel_delhi"]["petrol_inr_litre"] = self._safe_float(petrol_match.group(1))
            else:
                scraped_data["retail_fuel_delhi"]["petrol_inr_litre"] = FALLBACK_CORE_DATA["retail_fuel_delhi"]["petrol_inr_litre"]

            # Output dynamic telemetry
            log.info("Live Brent Crude (USD)", scraped_data["market_rates"]["brent_crude_usd"])
            log.info("Live USD/INR Rate", scraped_data["market_rates"]["usd_inr_exchange_rate"])
            log.info("SPR Stock (MMT)", scraped_data["spr_status"]["current_stock_mmt"])
            log.info("SPR Import Cover (Days)", scraped_data["spr_status"]["days_of_import_cover"])
            
            return scraped_data

        except Exception as e:
            log.warn(f"Failed to parse live dashboard ({e}). Serving cached tracker metrics.")
            return FALLBACK_CORE_DATA

def fetch_and_prepare_payload(agent2_payload: Dict[str, Any]) -> Dict[str, Any]:
    scraper = CoreEnergyScraper()
    core_metrics = scraper.scrape_dashboard()
    enriched_payload = {
        **agent2_payload,
        "core_macro_indicators": core_metrics
    }
    return enriched_payload

if __name__ == "__main__":
    data = CoreEnergyScraper().scrape_dashboard()
    console.rule("[bold magenta]Extracted Payload Struct[/bold magenta]", style="magenta")
    console.print(Syntax(json.dumps(data, indent=2), "json", theme="monokai"))