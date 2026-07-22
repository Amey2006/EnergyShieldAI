"""
Orchestrator
------------
Runs every agent on its own cadence using APScheduler, so fast-changing
sources (news) poll often and slow-changing sources (PPAC, EIA weekly
reports) don't hammer their servers for no reason.

Run this in one terminal; run `uvicorn main:app --reload` in another.
The two are decoupled on purpose - the API just reads whatever JSON files
are on disk, so a slow/failing agent never blocks the dashboard.
"""
import os
import sys
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from utils.logger import get_logger
from agents import news_agent, inventory_agent, india_trade_agent
from agents import market_intelligence_agent, shipping_agent
from agents import prediction_agent, recommendation_agent

log = get_logger("orchestrator")


def safe_run(agent_module, name: str):
    """Never let one agent's exception kill the whole scheduler."""
    try:
        agent_module.run_once()
    except Exception as e:
        log.error(f"[{name}] run failed: {e}")


def run_pipeline_cycle():
    """News -> (inventory/trade/shipping/market run independently) -> Prediction -> Recommendation.
    Prediction/Recommendation are re-run every cycle since they're cheap and
    depend on the freshest upstream JSON already on disk."""
    safe_run(prediction_agent, "prediction_agent")
    safe_run(recommendation_agent, "recommendation_agent")


def main():
    news_min = int(os.getenv("NEWS_POLL_MINUTES", 5))
    inv_hours = int(os.getenv("INVENTORY_POLL_HOURS", 6))
    trade_hours = int(os.getenv("TRADE_POLL_HOURS", 24))
    ship_min = int(os.getenv("SHIPPING_POLL_MINUTES", 15))
    pred_min = int(os.getenv("PREDICTION_POLL_MINUTES", 10))

    scheduler = BlockingScheduler()

    scheduler.add_job(lambda: safe_run(news_agent, "news_agent"),
                       "interval", minutes=news_min, next_run_time=None, id="news")
    scheduler.add_job(lambda: safe_run(inventory_agent, "inventory_agent"),
                       "interval", hours=inv_hours, id="inventory")
    scheduler.add_job(lambda: safe_run(india_trade_agent, "india_trade_agent"),
                       "interval", hours=trade_hours, id="trade")
    scheduler.add_job(lambda: safe_run(market_intelligence_agent, "market_intelligence_agent"),
                       "interval", hours=trade_hours, id="market_intel")
    scheduler.add_job(lambda: safe_run(shipping_agent, "shipping_agent"),
                       "interval", minutes=ship_min, id="shipping")
    scheduler.add_job(run_pipeline_cycle,
                       "interval", minutes=pred_min, id="prediction_recommendation")

    log.info("Orchestrator: running each agent once immediately, then on schedule...")
    for job_fn, name in [
        (lambda: safe_run(news_agent, "news_agent"), "news_agent"),
        (lambda: safe_run(inventory_agent, "inventory_agent"), "inventory_agent"),
        (lambda: safe_run(india_trade_agent, "india_trade_agent"), "india_trade_agent"),
        (lambda: safe_run(market_intelligence_agent, "market_intelligence_agent"), "market_intelligence_agent"),
        (lambda: safe_run(shipping_agent, "shipping_agent"), "shipping_agent"),
    ]:
        job_fn()
    run_pipeline_cycle()

    log.info("Orchestrator: initial run complete, entering scheduled loop (Ctrl+C to stop)")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Orchestrator: shutting down")


if __name__ == "__main__":
    main()
