# Energy Supply Chain Resilience System

Multi-agent system monitoring geopolitical/logistics risk to India's crude oil
supply chain, modelling disruption scenarios, and generating procurement
rerouting recommendations.

## Architecture

```
News Agent ─────────┐
Market Intel Agent ──┤
Inventory Agent ─────┼──► Prediction Agent ──► Recommendation Agent ──► FastAPI ──► React Dashboard
India Trade Agent ───┤          (ARIMA/GARCH)      (LLM + RAG)
Shipping Agent ──────┘
                     │
                     ▼
              ChromaDB (news RAG store)
```

Each agent is a standalone Python file. Agents communicate by writing/reading
JSON files under `backend/data/`. The orchestrator runs each agent on its own
schedule (news = every few minutes, EIA/PPAC = hourly/daily, since those
sources don't update every minute).

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp ../.env.example .env         # fill in your keys
python orchestrator.py          # starts the agent scheduler (run in one terminal)
uvicorn main:app --reload --port 8000   # starts the API (run in another terminal)
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## What you need to fill in / change

1. `.env` — add your free API keys (see `.env.example`).
2. `agents/india_trade_agent.py` and `agents/market_intelligence_agent.py` —
   these scrape PPAC / IEA-OPEC-EIA report pages. The HTML structure of
   government sites changes, so the CSS selectors here are placeholders.
   Run with `LOG_LEVEL=DEBUG` and look at the `[RAW MATCH]` log lines to see
   what's actually being picked up, then adjust the keyword/regex list —
   same iterative pattern you've been using for PPAC scraping.
3. `agents/shipping_agent.py` — AIS free tiers are rate-limited and change
   provider terms often; check whichever free AIS source you land on and
   adjust the request format.
4. `data/historical_brent.csv` — currently seeded with a small synthetic
   series so ARIMA/GARCH run out of the box. Replace with real historical
   Brent/WTI data (EIA has free historical series) for real forecasts.
5. `utils/llm_client.py` — set `LLM_PROVIDER` in `.env` to `grok`, `groq`, or
   `gemini`. Grok's API has no guaranteed permanent free tier, so `groq` or
   `gemini` are safer defaults if you want zero cost.

## Nothing else needs installing beyond what's in requirements.txt / package.json,
except Playwright's browser binary (`playwright install chromium`) and Node.js
18+ for the frontend.
