import os
import json
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class GeopoliticalRiskAgent:
    def __init__(self):
        self.name = "Geopolitical Risk Intelligence Agent (Task 1)"
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        # Initialize Groq client if key exists
        self.groq_client = None
        if self.groq_api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
            except Exception:
                self.groq_client = None

    def fetch_live_news(self, query: str = "crude oil OR strait of hormuz OR red sea OR opec") -> str:
        """
        Tier 1: Fetch live real-time news headlines using NewsAPI.org
        """
        if not self.news_api_key or self.news_api_key == "your_news_api_key_here":
            return None
            
        url = f"https://newsapi.org/v2/everything?q={requests.utils.quote(query)}&sortBy=publishedAt&pageSize=5&apiKey={self.news_api_key}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("articles", [])
                if articles:
                    headlines = [f"• {art['title']} - {art.get('source', {}).get('name', 'News')}" for art in articles if art.get('title')]
                    return "\n".join(headlines[:5])
        except Exception:
            pass
        return None

    def analyze_event(self, event_text: str = None, scenario: str = None) -> Dict[str, Any]:
        """
        Waterfall Pipeline:
        Tier 1: Fetch Live Real-Time News (NewsAPI) -> Analyze with Groq Llama-3.3-70B
        Tier 2: Fallback to Direct Groq LLM Threat Parsing on User Input
        Tier 3: Fallback to Deterministic Static Threat Matrix
        """
        input_signal = scenario or event_text or "Normal Operations"
        logs = [f"Task 1: Initiated Geopolitical Intelligence Pipeline for input: '{input_signal}'."]

        # =====================================================================
        # TIER 1: LIVE NEWS API (NewsAPI.org)
        # =====================================================================
        live_news_summary = self.fetch_live_news(query=f"{input_signal} OR crude oil OR strait of hormuz")
        using_tier1 = False
        
        analysis_text = input_signal
        if live_news_summary:
            using_tier1 = True
            analysis_text = f"User Scenario: {input_signal}\nLive Real-Time News Headlines:\n{live_news_summary}"
            logs.append("Task 1 [Tier 1 SUCCESS]: Fetched live real-time global news headlines via NewsAPI.")

        # =====================================================================
        # TIER 2: GROQ LLM INTELLIGENCE (Llama-3.3-70B)
        # =====================================================================
        if self.groq_client:
            try:
                prompt = f"""
                You are a Senior Geopolitical Risk Intelligence Analyst for Energy Security.
                Analyze the following threat intelligence signal & live news feed and return a JSON object:

                Context:
                {analysis_text}

                Return ONLY valid JSON matching this exact structure:
                {{
                    "geopolitical_event": "{input_signal}",
                    "risk_score": <float 0.0 to 100.0>,
                    "severity": "<Normal|Low|Medium|High|Critical>",
                    "strait_at_risk": "<Chokepoint Name e.g. Strait of Hormuz or Bab-el-Mandeb>",
                    "chokepoints": ["<list of chokepoints>"],
                    "affected_suppliers": ["<list of countries>"],
                    "affected_routes": ["<list of routes>"],
                    "organizations": ["<list of orgs>"],
                    "confidence_score": <float 0.0 to 1.0>,
                    "news_summary": "<brief 1-sentence synthesis of threat news>"
                }}
                """
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.groq_model,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                raw_json = chat_completion.choices[0].message.content
                parsed = json.loads(raw_json)

                r_score = float(parsed.get("risk_score", 50.0))
                if r_score <= 1.0:
                    r_score = r_score * 100.0

                data_source = "Tier 1: Live NewsAPI + Groq Llama-3.3-70B AI Analysis" if using_tier1 else "Tier 2: Direct Groq Llama-3.3-70B Threat Parsing"
                logs.append(f"Task 1 [{ 'Tier 1' if using_tier1 else 'Tier 2' } SUCCESS]: Generated AI Risk Score {round(r_score, 1)}/100 ({parsed.get('severity')}).")

                return {
                    "agent": self.name,
                    "geopolitical_event": parsed.get("geopolitical_event", input_signal),
                    "risk_score": round(r_score, 1),
                    "severity": parsed.get("severity", "Medium"),
                    "target_region": "Middle East / Maritime Chokepoints",
                    "strait_at_risk": parsed.get("strait_at_risk", "Strait of Hormuz"),
                    "chokepoints": parsed.get("chokepoints", ["Strait of Hormuz"]),
                    "affected_suppliers": parsed.get("affected_suppliers", ["Saudi Arabia", "Iraq"]),
                    "affected_routes": parsed.get("affected_routes", ["Persian Gulf"]),
                    "organizations": parsed.get("organizations", ["OPEC"]),
                    "confidence_score": float(parsed.get("confidence_score", 0.9)),
                    "news_feed": live_news_summary or "Real-time news stream active.",
                    "data_source": data_source,
                    "logs": logs
                }
            except Exception as e:
                logs.append(f"Task 1: Groq LLM parsing warning ({e}). Transitioning to Tier 3 Static Fallback.")

        # =====================================================================
        # TIER 3: STATIC DATA THREAT MATRIX (Offline Fallback)
        # =====================================================================
        logs.append("Task 1 [Tier 3 FALLBACK]: Utilizing Static Threat Data Matrix.")
        signal_lower = input_signal.lower()

        strait_at_risk = "Strait of Hormuz"
        severity = "Normal"
        risk_score = 15.0
        affected_suppliers = []
        affected_routes = []
        organizations = []
        chokepoints = []
        confidence = 0.85

        if "hormuz" in signal_lower:
            strait_at_risk = "Strait of Hormuz"
            chokepoints = ["Strait of Hormuz"]
            affected_suppliers = ["Saudi Arabia", "Iraq", "UAE", "Kuwait", "Qatar"]
            affected_routes = ["Persian Gulf Shipping Lane"]
            organizations = ["IRGC", "OPEC"]
            severity = "Critical" if "block" in signal_lower else "High"
            risk_score = 88.0 if "block" in signal_lower else 72.0
            confidence = 0.95

        elif "red sea" in signal_lower or "houthi" in signal_lower or "attack" in signal_lower:
            strait_at_risk = "Bab-el-Mandeb"
            chokepoints = ["Bab-el-Mandeb Strait", "Red Sea", "Suez Canal"]
            affected_suppliers = ["Saudi Arabia (Red Sea Yanbu)", "Russia"]
            affected_routes = ["Red Sea Route", "Suez Corridor"]
            organizations = ["Houthi Movement"]
            severity = "High"
            risk_score = 78.0
            confidence = 0.92

        elif "opec" in signal_lower or "cut" in signal_lower:
            strait_at_risk = "Persian Gulf"
            chokepoints = ["Strait of Hormuz"]
            affected_suppliers = ["Saudi Arabia", "UAE", "Iraq", "Russia"]
            affected_routes = ["Middle East Export Corridors"]
            organizations = ["OPEC+"]
            severity = "Medium"
            risk_score = 55.0
            confidence = 0.85

        elif "sanction" in signal_lower or "escalation" in signal_lower:
            strait_at_risk = "Strait of Hormuz"
            chokepoints = ["Strait of Hormuz", "Black Sea"]
            affected_suppliers = ["Russia", "Iran", "Venezuela"]
            affected_routes = ["Black Sea Corridor"]
            organizations = ["OFAC", "EU Council"]
            severity = "High"
            risk_score = 74.0
            confidence = 0.89

        return {
            "agent": self.name,
            "geopolitical_event": input_signal,
            "risk_score": risk_score,
            "severity": severity,
            "target_region": "Middle East / Maritime Chokepoints",
            "strait_at_risk": strait_at_risk,
            "chokepoints": chokepoints,
            "affected_suppliers": affected_suppliers,
            "affected_routes": affected_routes,
            "organizations": organizations,
            "confidence_score": confidence,
            "news_feed": "Static Threat Data Matrix Active.",
            "data_source": "Tier 3: Static Threat Data Matrix",
            "logs": logs
        }

def run_geopolitical_agent(event_text: str = None, scenario: str = None) -> Dict[str, Any]:
    agent = GeopoliticalRiskAgent()
    return agent.analyze_event(event_text=event_text, scenario=scenario)

if __name__ == "__main__":
    agent = GeopoliticalRiskAgent()
    res = agent.analyze_event(scenario="Strait of Hormuz partial blockage")
    print(json.dumps(res, indent=2))
