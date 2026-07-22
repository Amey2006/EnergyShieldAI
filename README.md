# ⚡ EnergyShield AI
### AI-Powered Multi-Agent Energy Supply Chain Resilience Platform

> **An intelligent decision support system that predicts energy supply disruptions, forecasts crude oil prices, analyzes geopolitical risks, and generates actionable recommendations using AI Agents, Machine Learning, Retrieval-Augmented Generation (RAG), and Time-Series Forecasting.**

---

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)
![Vite](https://img.shields.io/badge/Vite-Build-purple?logo=vite)
![Machine Learning](https://img.shields.io/badge/ML-ARIMA%20%7C%20GARCH-success)
![RAG](https://img.shields.io/badge/RAG-ChromaDB-orange)
![License](https://img.shields.io/badge/License-MIT-green)

</p>

---

# 📌 Problem Statement

Global energy supply chains are extremely vulnerable to:

- 🌍 Geopolitical conflicts
- 🚢 Shipping disruptions
- 🛢 Oil inventory shortages
- 📈 Extreme market volatility
- 🌪 Natural disasters
- 📉 Sudden crude price fluctuations

Organizations often rely on fragmented dashboards and manually interpret data from multiple sources, delaying critical decisions.

---

# 💡 Solution

**EnergyShield AI** combines multiple intelligent agents, statistical forecasting models, Retrieval-Augmented Generation (RAG), and Large Language Models to continuously monitor global energy markets and generate real-time recommendations for policymakers, refineries, and energy companies.

Instead of relying only on AI-generated text, the platform combines:

- Real-time data monitoring
- Statistical forecasting
- Risk scoring
- Knowledge retrieval
- Explainable AI recommendations

This ensures recommendations are grounded in data rather than hallucinated outputs.

---

# ✨ Key Features

- 📰 Live Geopolitical News Monitoring
- 🚢 Shipping Route Monitoring
- 🛢 Strategic Inventory Tracking
- 🇮🇳 India Import/Export Analysis
- 📈 Brent Crude Price Forecasting
- 📊 Market Volatility Prediction
- 🤖 AI Recommendation Engine
- 🧠 Retrieval-Augmented Generation (RAG)
- 📉 Risk Score Dashboard
- 🌍 Interactive Vessel Map
- 📊 Visual Analytics Dashboard
- ⚡ Automated Multi-Agent Scheduling

---

# 🏗 System Architecture

```text
                           External Data Sources
 ┌────────────────────────────────────────────────────────────┐
 │                                                            │
 │   News APIs      Shipping Data      Trade Reports          │
 │        Inventory Reports      Historical Oil Prices        │
 │                                                            │
 └──────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
                     Multi-Agent Intelligence Layer
 ┌────────────────────────────────────────────────────────────┐
 │                                                            │
 │  📰 News Agent                                              │
 │  🚢 Shipping Agent                                          │
 │  🛢 Inventory Agent                                         │
 │  🇮🇳 India Trade Agent                                      │
 │  📊 Market Intelligence Agent                              │
 │                                                            │
 └──────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
                     Prediction & Analytics Layer
 ┌────────────────────────────────────────────────────────────┐
 │                                                            │
 │            ARIMA Price Forecasting                         │
 │            GARCH Volatility Prediction                     │
 │            Risk Assessment Engine                          │
 │                                                            │
 └──────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
                     Knowledge Intelligence Layer
 ┌────────────────────────────────────────────────────────────┐
 │                                                            │
 │        ChromaDB Vector Store (RAG)                         │
 │        Relevant News Retrieval                             │
 │        Context Generation                                  │
 │                                                            │
 └──────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
                  AI Recommendation Generation Layer
 ┌────────────────────────────────────────────────────────────┐
 │                                                            │
 │         LLM Recommendation Agent                           │
 │         Procurement Suggestions                            │
 │         Risk Mitigation Strategies                         │
 │                                                            │
 └──────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
                     FastAPI REST Backend
                                │
                                ▼
                      React Dashboard (Frontend)
```

---

# 🔄 System Workflow

```text
Data Collection
      │
      ▼
Multi-Agent Monitoring
      │
      ▼
Risk Assessment
      │
      ▼
Price Forecasting
      │
      ▼
Store Knowledge in ChromaDB
      │
      ▼
Retrieve Relevant Context
      │
      ▼
LLM Recommendation Generation
      │
      ▼
Interactive Dashboard
```

---

# 🤖 Multi-Agent Architecture

## 📰 News Agent

Responsibilities

- Collects geopolitical news
- Detects supply chain disruptions
- Identifies refinery shutdowns
- Detects sanctions and wars

Output

- Risk events
- News summaries
- Event severity

---

## 🚢 Shipping Agent

Responsibilities

- Tracks crude oil transportation
- Monitors shipping disruptions
- Detects route delays

Output

- Shipping status
- Estimated delay
- Route risk

---

## 🛢 Inventory Agent

Responsibilities

- Monitors petroleum reserves
- Tracks inventory levels
- Detects shortages

Output

- Inventory statistics
- Supply buffer estimation

---

## 🇮🇳 India Trade Agent

Responsibilities

- Monitors crude imports
- Monitors exports
- Tracks dependency on suppliers

Output

- Trade metrics
- Import trends
- Country-wise analysis

---

## 📊 Market Intelligence Agent

Responsibilities

- Collects market indicators
- Monitors Brent prices
- Economic signals

Output

- Market sentiment
- Trend analysis

---

## 📈 Prediction Agent

Responsibilities

- Forecast future Brent prices
- Estimate volatility
- Calculate confidence intervals

Models Used

- ARIMA
- GARCH

Output

- Price Forecast
- Volatility Forecast
- Trend Direction

---

## 🤖 Recommendation Agent

Responsibilities

- Retrieves relevant events from ChromaDB
- Combines forecasting outputs
- Generates actionable recommendations

Output

- Procurement Strategy
- Risk Mitigation
- Executive Summary

---

# 🧠 AI Pipeline

```text
Historical Prices
        │
        ▼
ARIMA Forecasting
        │
        ▼
Predicted Prices

Historical Returns
        │
        ▼
GARCH Model
        │
        ▼
Volatility Prediction

News
Inventory
Trade
Shipping
        │
        ▼
Embedding Generation
        │
        ▼
ChromaDB
        │
        ▼
Relevant Context Retrieval
        │
        ▼
LLM Recommendation
```

---

# 📊 Technology Stack

| Category | Technology |
|-----------|------------|
| Frontend | React + Vite |
| Backend | FastAPI |
| AI | LLM |
| Vector Database | ChromaDB |
| ML Forecasting | ARIMA |
| Volatility | GARCH |
| Scheduler | APScheduler |
| Charts | Recharts |
| Maps | Leaflet |
| Language | Python |
| API | REST |

---

# 📁 Project Structure

```text
energy-resilience-system
│
├── backend
│   ├── agents
│   │   ├── news_agent.py
│   │   ├── shipping_agent.py
│   │   ├── inventory_agent.py
│   │   ├── india_trade_agent.py
│   │   ├── market_intelligence_agent.py
│   │   ├── prediction_agent.py
│   │   └── recommendation_agent.py
│   │
│   ├── rag
│   │   └── vector_store.py
│   │
│   ├── utils
│   ├── data
│   ├── orchestrator.py
│   ├── generate_seed_data.py
│   ├── requirements.txt
│   └── main.py
│
├── frontend
│   ├── src
│   │   ├── components
│   │   ├── App.jsx
│   │   └── api.js
│   │
│   ├── package.json
│   └── vite.config.js
│
├── docs
├── .env.example
└── README.md
```

---

# 📊 Dashboard Modules

The frontend provides

- Live Risk Gauge
- Brent Price Forecast Chart
- Inventory Analytics
- News Feed
- Interactive Vessel Map
- AI Recommendations
- Test News Input
- Historical Trend Visualization

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/energy-resilience-system.git

cd energy-resilience-system
```

---

## Backend

```bash
cd backend

pip install -r requirements.txt

python generate_seed_data.py

uvicorn main:app --reload
```

Backend runs at

```
http://localhost:8000
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at

```
http://localhost:5173
```

---



# 📡 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /dashboard | Dashboard Data |
| GET | /forecast | Price Forecast |
| GET | /recommendation | AI Recommendation |
| GET | /news | News Feed |
| GET | /inventory | Inventory Status |
| GET | /shipping | Shipping Information |

---

# 🧠 Why ARIMA + GARCH?

Unlike many AI applications that rely solely on LLMs, EnergyShield AI separates forecasting from explanation.

**ARIMA**
- Forecasts future crude oil prices using historical trends.

**GARCH**
- Estimates future market volatility.

**LLM**
- Converts analytical outputs into understandable recommendations.

This design improves transparency, explainability, and reliability.

---

# 📚 Why RAG?

Instead of depending only on the LLM's pre-trained knowledge, EnergyShield AI stores recent events in ChromaDB.

During recommendation generation:

- Relevant geopolitical events are retrieved.
- Only related context is passed to the LLM.
- Recommendations are grounded in factual evidence.

This reduces hallucinations and improves decision quality.

---

# ⚡ Scheduler

Agents operate independently using APScheduler.

Example schedule

| Agent | Frequency |
|--------|-----------|
| News Agent | Every 5 minutes |
| Shipping Agent | Every 15 minutes |
| Inventory Agent | Every 6 hours |
| Trade Agent | Daily |
| Prediction Agent | Daily |
| Recommendation Agent | After predictions |

---

# 🌍 Business Impact

EnergyShield AI enables organizations to:

- Reduce procurement risk
- Anticipate crude price fluctuations
- Improve supply chain resilience
- Optimize strategic petroleum reserves
- Respond faster to geopolitical crises
- Support evidence-based decision making

---

# 🚀 Future Enhancements

- Live AIS vessel tracking
- Satellite imagery integration
- Reinforcement Learning for procurement optimization
- Digital Twin of refinery operations
- Kafka-based agent communication
- Multi-country deployment
- Carbon emission optimization
- Predictive maintenance integration

---

# 🎯 Hackathon Highlights

- ✅ Multi-Agent AI Architecture
- ✅ Explainable AI
- ✅ Retrieval-Augmented Generation (RAG)
- ✅ Time-Series Forecasting
- ✅ Real-Time Dashboard
- ✅ Modular & Scalable Design
- ✅ FastAPI Backend
- ✅ React Frontend
- ✅ Enterprise-Oriented Architecture

---

# 👥 Team

**Team Name:** *Bit Manipulators*

Members

- Amey Mohite
- Shambhu Gaikwad
- Madanraj Sagar
- Harshad Khatale

---


# ⭐ Acknowledgements

Built with ❤️ for the Hackathon to demonstrate how AI, statistical forecasting, and intelligent agents can improve global energy supply chain resilience through explainable, data-driven decision support.
