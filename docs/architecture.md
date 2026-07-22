# Architecture Notes

## Data flow

```
News Agent ──┐
Market Intel ─┤
Inventory ────┼──► (written as JSON to backend/data/*.json)
India Trade ──┤
Shipping ─────┘
        │
        ▼
Prediction Agent (reads news_agent.json for corridor risk + historical_brent.csv)
        │
        ▼
Recommendation Agent (reads all upstream JSON + queries ChromaDB RAG store, calls LLM)
        │
        ▼
FastAPI (/api/dashboard aggregates all JSON files)
        │
        ▼
React dashboard (polls every 60s)
```

## Why statistics before LLM

The Prediction Agent is deliberately NOT an LLM call. It uses:
- ARIMA(2,1,2) for the trend/level forecast
- GARCH(1,1) for volatility (oil shocks cluster in time - a constant-variance
  model would understate near-term risk right after a disruption headline)
- A transparent, tunable elasticity table translating corridor disruption
  probability into a price adjustment, instead of asking an LLM to invent a
  number

The LLM (Recommendation Agent) only explains, prioritizes, and suggests
actions - grounded in the statistical output and retrieved news context, not
generating numbers itself. This is worth stating explicitly in a hackathon
pitch/demo - it's the main technical differentiator from "wrap GPT around a
prompt" style submissions.

## Why JSON files instead of a message queue

For a hackathon timeline, files-on-disk under `backend/data/` are the
simplest reliable message bus: every agent is independently runnable and
debuggable (`python agents/news_agent.py`), nothing needs a running broker,
and the FastAPI layer just reads whatever's freshest. If you have time and
want it to feel more "real system", swap this for Redis pub/sub without
changing any agent's internal logic - each agent's `run_once()` already
returns the dict it writes, so redirecting that write is a small change.

## Known rough edges to budget time for

- `india_trade_agent.py` and `market_intelligence_agent.py` scrape live
  government/org pages whose HTML changes; budget real debugging time here,
  not code-writing time.
- `shipping_agent.py` has no free live AIS wired up by default (see comments
  in the file) - it ships illustrative fallback vessel positions so the map
  isn't empty during a demo. Wiring a real free AIS source is the single
  highest-effort remaining piece if you want it fully live.
- `historical_brent.csv` is synthetic. Replace with real EIA historical
  daily Brent spot price data before you trust the ARIMA/GARCH numbers in a
  real demo.
