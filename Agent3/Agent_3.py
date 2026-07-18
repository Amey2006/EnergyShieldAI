
import os
import sys
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

    class PlaywrightTimeoutError(Exception):
        """Stand-in so `except PlaywrightTimeoutError` still works when
        Playwright itself isn't installed."""
        pass

# =====================================================================
# 🔥 BULLETPROOF MONKEY-PATCH FOR GROQ/LITELLM CACHE BREAKPOINT BUG 🔥
# =====================================================================
import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

try:
    import crewai.experimental.agent_executor as _exp_exec
    _exp_exec.mark_cache_breakpoint = lambda msg: msg
except ImportError:
    pass

try:
    import crewai.agents.crew_agent_executor as _crew_exec
    _crew_exec.mark_cache_breakpoint = lambda msg: msg
except ImportError:
    pass
# =====================================================================

from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

# =====================================================================
# 🌐 IMPORT THE CORE ENERGY SCRAPER
# =====================================================================
try:
    from core_energy_scraper import CoreEnergyScraper
    CORE_SCRAPER_AVAILABLE = True
except ImportError:
    CORE_SCRAPER_AVAILABLE = False

load_dotenv()

# ==========================================
# INITIALIZE THE GROQ BRAIN (NATIVE WAY)
# ==========================================
groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.2
)

console = Console()

# =====================================================================
# 🎨 STRUCTURED / COLOURED LOGGER
# =====================================================================
class AgentLogger:
    """Rich-powered structured logger giving Agent 3 the same colourful,
    scannable terminal presence as Agent 2's verbose CrewAI output."""

    @staticmethod
    def banner(title: str):
        console.rule(f"[bold cyan]{title}[/bold cyan]", style="cyan")

    @staticmethod
    def step(msg: str):
        console.print(f"[bold blue]→[/bold blue] {msg}")

    @staticmethod
    def info(msg: str):
        console.print(f"  [dim]•[/dim] {msg}")

    @staticmethod
    def success(msg: str):
        console.print(f"  [bold green]✓[/bold green] {msg}")

    @staticmethod
    def warn(msg: str):
        console.print(f"  [bold yellow]⚠[/bold yellow] [yellow]{msg}[/yellow]")

    @staticmethod
    def error(msg: str):
        console.print(f"  [bold red]✗[/bold red] [red]{msg}[/red]")

    @staticmethod
    def raw_match(name: str, cells: list, value: str, mapped_to: str):
        console.print(
            f"  [magenta][RAW MATCH][/magenta] "
            f"[white]{name}[/white] -> [bold green]{value}[/bold green] "
            f"[dim](mapped to '{mapped_to}')[/dim]"
        )


log = AgentLogger()

# ==========================================
# CONSTANTS & PRICING/INVENTORY CONFIGURATION
# ==========================================
MT_TO_BBL = 7.33
PPAC_URL = "https://ppac.gov.in/production/crude-processing"
GLOBAL_DAILY_SUPPLY_BBL = 100_000_000

DEFAULT_BASE_BRENT = 78.00
DEFAULT_RISK_MULTIPLIER = 1.25
DEFAULT_ELASTICITY_FACTOR = 0.15

BASELINE_REFINERY_DB = {
    "Reliance Jamnagar": {
        "monthly_crude_processed_kmt": 3200.0,
        "stock_buffer_days_of_supply": 18,
        "spr_allocation_bbl": 0.0,
    },
    "Nayara Vadinar": {
        "monthly_crude_processed_kmt": 800.0,
        "stock_buffer_days_of_supply": 15,
        "spr_allocation_bbl": 0.0,
    },
    "CPCL Manali": {
        "monthly_crude_processed_kmt": 900.0,
        "stock_buffer_days_of_supply": 14,
        "spr_allocation_bbl": 0.0,
    },
    "IOCL Koyali": {
        "monthly_crude_processed_kmt": 1350.0,
        "stock_buffer_days_of_supply": 16,
        "spr_allocation_bbl": 0.0,
    },
}

# The default SPR stock (approx 39,000,000 bbl) used if the live dashboard is unavailable
DEFAULT_SPR_STOCK_BBL = 39_000_000.0

REFINERY_MATCH_KEYWORDS = {
    "Reliance Jamnagar": [["ril", "jamnagar"], ["reliance", "jamnagar"]],
    "Nayara Vadinar": [["nayara", "vadinar"], ["essar", "vadinar"], ["nel", "vadinar"]],
    "CPCL Manali": [["cpcl", "manali"]],
    "IOCL Koyali": [["iocl", "koyali"], ["iocl", "gujarat", "koyali"]],
}


# ==========================================
# LIVE PPAC SCRAPER
# ==========================================
class PPACScraper:
    def __init__(self, url: str = PPAC_URL, timeout_ms: int = 20_000):
        self.url = url
        self.timeout_ms = timeout_ms

    def _render_with_playwright(self) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Agent3-ResilienceBot/1.0; +headless)"
                )
                log.step("Launching headless Chromium and navigating to PPAC...")
                page.goto(self.url, timeout=self.timeout_ms, wait_until="domcontentloaded")

                log.step("Waiting for AJAX-rendered crude-processing table to populate...")
                page.wait_for_function(
                    """() => {
                        const cells = document.querySelectorAll('table tbody td');
                        return Array.from(cells).some(td => td.textContent.trim().length > 0);
                    }""",
                    timeout=self.timeout_ms,
                )
                html = page.content()
                log.success("Table populated — captured rendered HTML.")
                return html
            finally:
                browser.close()

    def scrape_ppac_statistics(self) -> dict:
        log.step(f"Connecting to PPAC data source: [underline]{self.url}[/underline]")

        if not PLAYWRIGHT_AVAILABLE:
            log.warn(
                "Playwright is not installed (pip install playwright && "
                "playwright install chromium). Switching to local baseline fallback database."
            )
            return BASELINE_REFINERY_DB

        try:
            html = self._render_with_playwright()
            log.step("Parsing rendered HTML tables...")

            soup = BeautifulSoup(html, "html.parser")
            tables = soup.find_all("table")
            if not tables:
                raise ValueError("No <table> elements found on PPAC page — layout may have changed.")

            parsed = {}
            all_labels_seen = []
            for table in tables:
                for row in table.find_all("tr"):
                    cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                    if len(cells) < 2:
                        continue
                    name = cells[0]
                    if not name:
                        continue
                    all_labels_seen.append(name)

                    name_lower = name.lower()
                    if "total" in name_lower:
                        continue

                    value = None
                    for cell in reversed(cells[1:-1] if len(cells) > 2 else cells[1:]):
                        cleaned = cell.replace(",", "").strip()
                        if cleaned and cleaned.replace(".", "", 1).isdigit():
                            value = cleaned
                            break
                    if value is None:
                        continue

                    for known_refinery, keyword_sets in REFINERY_MATCH_KEYWORDS.items():
                        matched = any(
                            all(kw in name_lower for kw in kw_set)
                            for kw_set in keyword_sets
                        )
                        if matched:
                            log.raw_match(name, cells, value, known_refinery)
                            prior = parsed.get(known_refinery, {}).get("monthly_crude_processed_kmt", 0.0)
                            parsed[known_refinery] = {
                                "monthly_crude_processed_kmt": prior + float(value)
                            }

            if parsed:
                log.success(
                    f"Final summed monthly totals: "
                    f"{ {k: v['monthly_crude_processed_kmt'] for k, v in parsed.items()} }"
                )

            unmatched_targets = set(BASELINE_REFINERY_DB) - set(parsed)
            if unmatched_targets:
                log.warn(
                    f"No live match found for: {sorted(unmatched_targets)}. "
                    f"All {len(all_labels_seen)} row labels PPAC returned this run: {all_labels_seen}"
                )

            if not parsed:
                raise ValueError("Parsed zero recognizable refinery rows from rendered PPAC table.")

            log.success(
                f"Live-matched {len(parsed)}/{len(BASELINE_REFINERY_DB)} refineries: {sorted(parsed)}. "
                f"Remaining {len(unmatched_targets)} still use baseline: {sorted(unmatched_targets)}"
            )
            merged = {}
            for name, base in BASELINE_REFINERY_DB.items():
                merged[name] = {**base, **parsed.get(name, {})}
            return merged

        except PlaywrightTimeoutError as exc:
            log.warn(f"PPAC page/table did not render in time ({exc}). Switching to local baseline fallback database.")
            return BASELINE_REFINERY_DB
        except Exception as exc:
            log.warn(f"Live PPAC scrape failed ({exc}). Switching to local baseline fallback database.")
            return BASELINE_REFINERY_DB


# ==========================================
# ECONOMIC / INVENTORY MATH
# ==========================================
class EconomicCalculator:
    """Deterministic math utilities — no LLM guesswork, pure arithmetic."""

    @staticmethod
    def predict_brent_price(
        delayed_capacity_bbl: float,
        base_price: float = DEFAULT_BASE_BRENT,
        risk_multiplier: float = DEFAULT_RISK_MULTIPLIER,
        elasticity_factor: float = DEFAULT_ELASTICITY_FACTOR,
        global_daily_supply_bbl: float = GLOBAL_DAILY_SUPPLY_BBL,
    ) -> dict:
        shock_ratio = (delayed_capacity_bbl / global_daily_supply_bbl) * risk_multiplier * elasticity_factor
        predicted_price = base_price * (1 + shock_ratio)
        absolute_increase = predicted_price - base_price
        percentage_increase = (absolute_increase / base_price) * 100
        return {
            "base_brent_price_usd": round(base_price, 2),
            "predicted_brent_price_usd": round(predicted_price, 2),
            "absolute_increase_usd": round(absolute_increase, 2),
            "percentage_increase": round(percentage_increase, 4),
        }

    @staticmethod
    def days_of_cover(stock_bbl: float, daily_demand_bbl: float) -> float:
        if daily_demand_bbl <= 0:
            return float("inf")
        return round(stock_bbl / daily_demand_bbl, 2)

    @staticmethod
    def assess_stockout_risk(doc: float, transit_delay_days: int) -> str:
        if doc < transit_delay_days:
            return "CRITICAL"
        elif doc <= transit_delay_days + 3:
            return "MEDIUM"
        else:
            return "LOW"


# ==========================================
# CORE AGENT 3 LOGIC
# ==========================================
@dataclass
class Agent3PriceInventoryAgent:
    base_brent_price: float = DEFAULT_BASE_BRENT
    risk_multiplier: float = DEFAULT_RISK_MULTIPLIER
    elasticity_factor: float = DEFAULT_ELASTICITY_FACTOR
    spr_stock_bbl: float = DEFAULT_SPR_STOCK_BBL
    scraper: PPACScraper = field(default_factory=PPACScraper)
    calc: EconomicCalculator = field(default_factory=EconomicCalculator)

    def __post_init__(self):
        """
        Dynamically updates the base pricing and SPR metrics using the 
        live dashboard scraper if available. (Option A implementation)
        """
        if CORE_SCRAPER_AVAILABLE:
            log.step("Initializing live macro constants from 'https://energy.thecore.in/'...")
            try:
                core_scraper = CoreEnergyScraper()
                live_data = core_scraper.scrape_dashboard()
                
                # Dynamic override of Brent crude spot price
                live_brent = live_data.get("market_rates", {}).get("brent_crude_usd")
                if live_brent:
                    self.base_brent_price = float(live_brent)
                    log.success(f"Overrode static baseline Brent with live spot rate: ${self.base_brent_price}/bbl")
                
                # Dynamic override of Strategic Petroleum Reserve Stock
                live_spr_mmt = live_data.get("spr_status", {}).get("current_stock_mmt")
                if live_spr_mmt:
                    # Conversion: MMT -> MT (* 1,000,000) -> bbl (* 7.33)
                    self.spr_stock_bbl = float(live_spr_mmt) * 1_000_000.0 * MT_TO_BBL
                    log.success(f"Overrode baseline SPR stock with live figure: {self.spr_stock_bbl:,.0f} bbl ({live_spr_mmt} MMT)")
            except Exception as e:
                log.warn(f"Could not load live dashboard parameters ({e}). Utilizing default static constants.")

    def _resolve_refinery_stats(self, refinery_db: dict, refinery_name: str) -> dict:
        entry = refinery_db.get(refinery_name)
        if entry is None:
            log.warn(f"Refinery '{refinery_name}' not found in scraped/baseline DB — using conservative estimate.")
            entry = {"monthly_crude_processed_kmt": 500.0, "stock_buffer_days_of_supply": 12}

        monthly_kmt = entry["monthly_crude_processed_kmt"]
        monthly_mt = monthly_kmt * 1000.0
        monthly_bbl = monthly_mt * MT_TO_BBL
        daily_demand_bbl = monthly_bbl / 30.0

        buffer_days = entry.get("stock_buffer_days_of_supply", 12)
        current_stock_bbl = daily_demand_bbl * buffer_days

        return {
            "daily_demand_bbl": round(daily_demand_bbl, 2),
            "current_stock_bbl": round(current_stock_bbl, 2),
        }

    def process(self, agent2_payload: dict) -> dict:
        chokepoint = agent2_payload.get("chokepoint", "Unknown Chokepoint")
        log.banner(f"Agent 3 — Processing '{chokepoint}'")

        shipping = agent2_payload.get("shipping_status", {})
        india_impact = agent2_payload.get("india_impact", {})
        logistics = agent2_payload.get("logistics", {})

        delayed_capacity_bbl = float(shipping.get("delayed_capacity_bbl", 0))
        transit_delay_days = int(logistics.get("additional_transit_days", 0))
        affected_refineries = india_impact.get("affected_refineries", [])

        log.banner("Step 1/4 — Refinery Statistics")
        refinery_db = self.scraper.scrape_ppac_statistics()

        log.banner("Step 2/4 — Price Shock Model")
        log.info(
            f"delayed_capacity_bbl={delayed_capacity_bbl:,.0f} | "
            f"global_daily_supply_bbl={GLOBAL_DAILY_SUPPLY_BBL:,.0f} | "
            f"risk_multiplier={self.risk_multiplier:.2f} | elasticity={self.elasticity_factor:.2f}"
        )
        pricing_impact = self.calc.predict_brent_price(
            delayed_capacity_bbl=delayed_capacity_bbl,
            base_price=self.base_brent_price,
            risk_multiplier=self.risk_multiplier,
            elasticity_factor=self.elasticity_factor,
        )
        log.success(
            f"Predicted Brent price: ${pricing_impact['predicted_brent_price_usd']:.2f}/bbl "
            f"(+{pricing_impact['percentage_increase']:.2f}%)"
        )

        log.banner("Step 3/4 — Refinery-Level Inventory Stress")
        refinery_level_stress = []
        total_stock = 0.0
        total_demand = 0.0

        stress_table = Table(show_header=True, header_style="bold cyan")
        stress_table.add_column("Refinery")
        stress_table.add_column("Stock (bbl)", justify="right")
        stress_table.add_column("Demand (bbl/day)", justify="right")
        stress_table.add_column("DoC (days)", justify="right")
        stress_table.add_column("Risk", justify="center")

        risk_colors = {"CRITICAL": "bold red", "MEDIUM": "bold yellow", "LOW": "bold green"}

        for refinery_name in affected_refineries:
            stats = self._resolve_refinery_stats(refinery_db, refinery_name)
            doc = self.calc.days_of_cover(stats["current_stock_bbl"], stats["daily_demand_bbl"])
            risk = self.calc.assess_stockout_risk(doc, transit_delay_days)

            stress_table.add_row(
                refinery_name,
                f"{stats['current_stock_bbl']:,.0f}",
                f"{stats['daily_demand_bbl']:,.0f}",
                f"{doc:.2f}",
                f"[{risk_colors[risk]}]{risk}[/{risk_colors[risk]}]",
            )

            refinery_level_stress.append({
                "refinery_name": refinery_name,
                "current_stock_bbl": stats["current_stock_bbl"],
                "daily_demand_bbl": stats["daily_demand_bbl"],
                "days_of_cover": doc,
                "rerouting_delay_days": transit_delay_days,
                "stockout_risk": risk,
            })
            total_stock += stats["current_stock_bbl"]
            total_demand += stats["daily_demand_bbl"]

        console.print(stress_table)

        log.banner("Step 4/4 — National Inventory Rollup")
        national_doc = self.calc.days_of_cover(total_stock + self.spr_stock_bbl, total_demand)
        national_inventory = {
            "total_refinery_stock_bbl": round(total_stock, 2),
            "total_spr_stock_bbl": self.spr_stock_bbl,
            "national_daily_demand_bbl": round(total_demand, 2),
            "national_days_of_cover_remaining": national_doc,
        }
        log.success(f"National DoC (refinery stock + SPR): {national_inventory['national_days_of_cover_remaining']:.2f} days")
        console.rule(f"[bold cyan]Agent 3 complete for '{chokepoint}'[/bold cyan]", style="cyan")

        return {
            "chokepoint": chokepoint,
            "pricing_impact": pricing_impact,
            "national_inventory": national_inventory,
            "refinery_level_stress": refinery_level_stress,
        }


# ==========================================
# CREWAI TOOL WRAPPER
# ==========================================
@tool("Run Price and Inventory Resilience Analysis")
def run_price_inventory_analysis_tool(agent2_payload_json: str) -> str:
    """
    Consumes Agent 2's (Shipping Agent) structured JSON payload describing a
    chokepoint disruption, cross-references it against live/baseline Indian
    refinery crude-processing statistics, and returns Agent 3's structured
    JSON payload: price-shock prediction, national inventory rollup, and
    per-refinery days-of-cover / stockout risk. All math is deterministic
    Python — the LLM must not recompute or alter these figures.
    """
    try:
        payload = json.loads(agent2_payload_json)
    except (json.JSONDecodeError, TypeError):
        return json.dumps({"error": "agent2_payload_json must be a valid JSON string"})

    agent3 = Agent3PriceInventoryAgent()
    result = agent3.process(payload)
    return json.dumps(result)


# ==========================================
# AGENT 3 DEFINITION
# ==========================================
def run_price_inventory_agent(agent2_payload: Dict[str, Any]) -> str:
    """
    Accepts Agent 2's structured output dictionary and executes the Price and
    Inventory Resilience Agent to yield Agent 3's structured JSON payload
    for Agent 4 (The Scenario Simulator).
    """
    agent2_payload_json = json.dumps(agent2_payload)
    chokepoint = agent2_payload.get("chokepoint", "Strait of Hormuz")

    price_inventory_agent = Agent(
        role="Price and Inventory Resilience Analyst",
        goal=(
            f"Translate Agent 2's shipping disruption data for {chokepoint} into hard economic "
            f"and physical inventory risk metrics for Indian refineries, using deterministic math only."
        ),
        backstory=(
            "You are a highly analytical energy economist specializing in Indian refinery crude "
            "supply chains. You cross-reference live PPAC (Petroleum Planning & Analysis Cell) "
            "processing statistics against maritime disruption data, computing Brent price shocks "
            "and refinery days-of-cover with zero tolerance for mathematical guesswork — every "
            "number must come from the tool's deterministic calculations, never estimated by you."
        ),
        tools=[run_price_inventory_analysis_tool],
        llm=groq_llm,
        verbose=True,
        allow_delegation=False,
    )

    price_inventory_task = Task(
        description=(
            f"Agent 2 has produced the following shipping/disruption intelligence payload for "
            f"'{chokepoint}':\n\n{agent2_payload_json}\n\n"
            f"Your Instructions:\n"
            f"1. Call the 'Run Price and Inventory Resilience Analysis' tool, passing the exact "
            f"   JSON payload above as the 'agent2_payload_json' argument.\n"
            f"2. Do NOT recalculate, estimate, or alter any numeric value the tool returns — the "
            f"   tool performs all pricing and inventory math deterministically.\n"
            f"3. Return the tool's JSON output exactly as-is.\n\n"
            f"CRITICAL FORMATTING RULES:\n"
            f"Output MUST be ONLY the valid raw JSON object returned by the tool. Do not wrap it "
            f"in markdown code fences or add any conversational text."
        ),
        expected_output="A single structured JSON string matching Agent 3's output schema.",
        agent=price_inventory_agent,
    )

    price_inventory_crew = Crew(
        agents=[price_inventory_agent],
        tasks=[price_inventory_task],
        verbose=True,
        share_crew=False,
    )

    result = price_inventory_crew.kickoff()
    return result


# ==========================================
# LOCAL TESTING & INTEGRATION
# ==========================================
if __name__ == "__main__":
    console.print(Panel.fit(
        "🚦 [bold]Initiating Integration Test for Agent 3[/bold]\n"
        "Price and Inventory Resilience Agent (Option A Live Core Integration)",
        border_style="cyan",
    ))

    mock_agent2_output = {
        "chokepoint": "Strait of Hormuz",
        "risk_level": "High",
        "shipping_status": {
            "total_tankers": 30,
            "delayed_tankers": 15,
            "average_delay_days": 7,
            "delayed_capacity_bbl": 22500000,
        },
        "india_impact": {
            "affected_ports": ["Mundra", "Jamnagar", "Sikka"],
            "affected_refineries": ["Reliance Jamnagar", "Nayara Vadinar"],
            "estimated_supply_loss_percent": 50,
        },
        "logistics": {
            "recommended_route": "Cape of Good Hope",
            "additional_transit_days": 12,
        },
        "confidence": 0.8,
    }

    final_analysis = run_price_inventory_agent(mock_agent2_output)

    console.rule("[bold cyan]FINAL AGENT 3 OUTPUT[/bold cyan]", style="cyan")
    try:
        parsed = json.loads(str(final_analysis))
        console.print(Syntax(json.dumps(parsed, indent=2), "json", theme="monokai", line_numbers=False))
    except (json.JSONDecodeError, TypeError):
        console.print(final_analysis)
    console.rule(style="cyan")