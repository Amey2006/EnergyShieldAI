import os
import requests
from typing import List, Dict, Any
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# =====================================================================
# 🔥 BULLETPROOF MONKEY-PATCH FOR GROQ/LITELLM CACHE BREAKPOINT BUG 🔥
# =====================================================================
import crewai.llms.cache as _crewai_cache
# 1. Patch the source function
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

# 2. Patch where it gets bound in the execution environments
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

# Now import the rest of your CrewAI components safely
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
# Load environmental variables
load_dotenv()

# ==========================================
# INITIALIZE THE GEMINI BRAIN (NATIVE WAY)
# ==========================================
groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.2
)       

# ==========================================
# CONSTANTS & COORDINATE CONFIGURATION
# ==========================================
CHOKE_POINTS = {
    "Strait of Hormuz": {
        "lat_bottom": 25.5, "lat_top": 27.5,   # Expanded from 26.0-27.0
        "lon_left": 55.0, "lon_right": 57.0,   # Expanded from 55.8-56.8
        "choke_point_name": "Strait of Hormuz"
    },
    "Bab-el-Mandeb": {
        "lat_bottom": 11.5, "lat_top": 13.5,   # Expanded from 12.1-13.1
        "lon_left": 42.0, "lon_right": 44.0,   # Expanded from 42.8-43.8
        "choke_point_name": "Bab-el-Mandeb Strait"
    },
    "Strait of Malacca": {
        "lat_bottom": 1.0, "lat_top": 3.0,     # Expanded from 1.1-2.3
        "lon_left": 101.5, "lon_right": 103.5, # Expanded from 102.5-103.7
        "choke_point_name": "Strait of Malacca"
    }
}
# Fallback Database for Local/Offline Resilient Development
FALLBACK_VESSEL_DATABASE = {
    "Strait of Hormuz": [
        {"name": "Al-Mubarak", "mmsi": "477045900", "status": "Delayed", "delay_days": 8, "cargo_capacity": "2,000,000 bbl", "destination": "Sikka Port, India"},
        {"name": "Oceanic Sovereign", "mmsi": "235118000", "status": "Delayed", "delay_days": 10, "cargo_capacity": "1,800,000 bbl", "destination": "Jamnagar, India"},
        {"name": "Shakti Prasad", "mmsi": "419001234", "status": "Underway", "delay_days": 0, "cargo_capacity": "2,200,000 bbl", "destination": "Paradip, India"},
        {"name": "Hormuz Sentinel", "mmsi": "636018901", "status": "Delayed", "delay_days": 5, "cargo_capacity": "1,500,000 bbl", "destination": "Mumbai, India"}
    ],
    "Bab-el-Mandeb": [
        {"name": "Suez Pathfinder", "mmsi": "311000123", "status": "Delayed", "delay_days": 12, "cargo_capacity": "1,700,000 bbl", "destination": "Mundra, India"},
        {"name": "Red Sea Jewel", "m478msi": "248112000", "status": "Underway", "delay_days": 0, "cargo_capacity": "2,000,000 bbl", "destination": "Visakhapatnam, India"}
    ],
    "Strait of Malacca": [
        {"name": "Malacca Voyager", "mmsi": "563009800", "status": "Underway", "delay_days": 0, "cargo_capacity": "2,100,000 bbl", "destination": "Chennai, India"},
        {"name": "Sumatra Trader", "mmsi": "525012345", "status": "Delayed", "delay_days": 3, "cargo_capacity": "1,200,000 bbl", "destination": "Haldia, India"}
    ]
}

@tool("Track Shipping Vessels in Chokepoint")
def track_shipping_vessels_tool(choke_point_name: str) -> str:
    """
    Queries real-time AIS vessel tracking data in a given maritime choke point.
    Returns a JSON string containing the vessel list and calculated supply loss metrics.
    """
    api_key = os.getenv("VESSELAPI_API_KEY")
    coords = CHOKE_POINTS.get(choke_point_name)
    
    # 1. Fetch raw data (API or Fallback)
    raw_vessel_list = []
    using_fallback = False

    if not api_key or api_key == "your_real_vesselapi_api_key_here":
        raw_vessel_list = FALLBACK_VESSEL_DATABASE.get(choke_point_name, [])
        using_fallback = True
    else:
        base_url = "https://api.vesselapi.com/v1/location/vessels/bounding-box"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {
            "filter.latBottom": coords["lat_bottom"],
            "filter.latTop": coords["lat_top"],
            "filter.lonLeft": coords["lon_left"],
            "filter.lonRight": coords["lon_right"],
            "pagination.limit": 50
        }
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                raw_vessels = data.get("vessels", [])
                
                # Parse live API vessels into standard dict
                for item in raw_vessels:
                    speed = float(item.get("speed", 0))
                    is_delayed = speed < 1.5 and item.get("nav_status") != "moored"
                    deadweight = item.get("deadweight")
                    capacity_str = f"{deadweight * 7.3:,.0f} bbl" if deadweight else "1,500,000 bbl"
                    
                    raw_vessel_list.append({
                        "name": item.get("vessel_name") or item.get("name") or "Unknown Vessel",
                        "status": "Delayed" if is_delayed else "Underway",
                        "delay_days": item.get("delay_days", 0) if is_delayed else 0,
                        "cargo_capacity": capacity_str,
                        "destination": item.get("reported_destination") or item.get("destination") or "India Port"
                    })
            else:
                using_fallback = True
        except Exception:
            using_fallback = True

    if using_fallback and not raw_vessel_list:
        raw_vessel_list = FALLBACK_VESSEL_DATABASE.get(choke_point_name, [])

    # =====================================================================
    # ⚙️ MATHEMATICAL CALCULATION OF SUPPLY LOSS
    # =====================================================================
    total_transit_capacity = 0
    delayed_capacity = 0
    total_delay_days = 0
    delayed_tanker_count = 0

    for vessel in raw_vessel_list:
        # Clean numeric capacity value (remove ' bbl' and commas to convert to int)
        cap_str = vessel.get("cargo_capacity", "0").replace(" bbl", "").replace(",", "")
        capacity_bbl = int(cap_str) if cap_str.isdigit() else 1500000 # fallback if parse fails
        
        total_transit_capacity += capacity_bbl

        if vessel.get("status") == "Delayed":
            delayed_capacity += capacity_bbl
            delayed_tanker_count += 1
            total_delay_days += vessel.get("delay_days", 0)

    # Apply Formula: (Delayed / Total) * 100
    supply_loss_percent = 0
    if total_transit_capacity > 0:
        supply_loss_percent = round((delayed_capacity / total_transit_capacity) * 100)

    avg_delay_days = round(total_delay_days / delayed_tanker_count) if delayed_tanker_count > 0 else 0

    # 2. Package everything neatly for the LLM Agent
    analysis_payload = {
        "vessels_tracked": raw_vessel_list,
        "calculated_metrics": {
            "total_tankers": len(raw_vessel_list),
            "delayed_tankers": delayed_tanker_count,
            "average_delay_days": avg_delay_days,
            "delayed_capacity_bbl": delayed_capacity,
            "estimated_supply_loss_percent": supply_loss_percent
        }
    }

    return str(analysis_payload)
# ==========================================
# AGENT 2 DEFINITION
# ==========================================
def run_shipping_agent(upstream_news_payload: Dict[str, Any]) -> str:
    """
    Accepts the upstream output dictionary and executes the Shipping Resilience Agent
    to yield an advanced multi-tiered JSON intelligence payload.
    """
    target_choke_point = upstream_news_payload.get("strait_at_risk", "Strait of Hormuz")
    threat_description = upstream_news_payload.get("geopolitical_event", "General tension")
    risk_score = upstream_news_payload.get("risk_score", 0.5)

    # Initialize shipping Agent powered by Gemini natively
    shipping_agent = Agent(
        role="Senior Maritime Logistics & Shipping Supply Chain Risk Analyst",
        goal=f"Analyze crude oil tanker tracks around {target_choke_point} to assess supply losses to specific Indian ports and refineries.",
        backstory=(
            "You are a master of global maritime logistics, petroleum trade flows, and down-stream refinery interdependencies. "
            "You map physical shipping bottlenecks and alternative routes (like the Cape of Good Hope) directly to operational impacts "
            "at Indian refining giants (e.g., Reliance Jamnagar, Nayara Vadinar, IOCL Paradip)."
        ),
        tools=[track_shipping_vessels_tool],
        llm=groq_llm,
        verbose=True,
        allow_delegation=False
    )
    shipping_analysis_task = Task(
        description=(
            f"An upstream threat intel alert has flagged high risk at {target_choke_point}.\n"
            f"Threat Context: '{threat_description}' (Risk Score: {risk_score * 100}%)\n\n"
            f"Your Instructions:\n"
            f"1. Run the 'Track Shipping Vessels in Chokepoint' tool for '{target_choke_point}'.\n"
            f"2. Use the exact math calculations returned in the tool's 'calculated_metrics' payload "
            f"   to fill out the 'shipping_status' metrics and 'estimated_supply_loss_percent'. Do not recalculate them.\n"
            f"3. Evaluate the downstream 'india_impact' by mapping ports to their corresponding refineries.\n"
            f"4. Propose fallback 'logistics' routes and standard additional maritime transit days.\n"
            f"5. Provide a 'confidence' score between 0.0 and 1.0 reflecting data completeness.\n\n"
            f"CRITICAL FORMATTING RULES:\n"
            f"Output MUST be ONLY a valid raw JSON object matching this exact structure:\n"
            f"{{\n"
            f"  \"chokepoint\": \"{target_choke_point}\",\n"
            f"  \"risk_level\": \"High\",\n"
            f"  \"shipping_status\": {{\n"
            f"    \"total_tankers\": <Use 'total_tankers' from tool>,\n"
            f"    \"delayed_tankers\": <Use 'delayed_tankers' from tool>,\n"
            f"    \"average_delay_days\": <Use 'average_delay_days' from tool>,\n"
            f"    \"delayed_capacity_bbl\": <Use 'delayed_capacity_bbl' from tool>\n"
            f"  }},\n"
            f"  \"india_impact\": {{\n"
            f"    \"affected_ports\": [<list of strings>],\n"
            f"    \"affected_refineries\": [<list of strings>],\n"
            f"    \"estimated_supply_loss_percent\": <Use 'estimated_supply_loss_percent' from tool>\n"
            f"  }},\n"
            f"  \"logistics\": {{\n"
            f"    \"recommended_route\": \"<route string>\",\n"
            f"    \"additional_transit_days\": <integer>\n"
            f"  }},\n"
            f"  \"confidence\": <float>\n"
            f"}}"
        ),
        expected_output="A single structured JSON string.",
        agent=shipping_agent
    )
    # Assemble Crew with telemetry warning hidden
    shipping_crew = Crew(
        agents=[shipping_agent],
        tasks=[shipping_analysis_task],
        verbose=True,
        share_crew=False  # Clean terminal output
    )

    result = shipping_crew.kickoff()
    return result


# ==========================================
# LOCAL TESTING & INTEGRATION
# ==========================================
if __name__ == "__main__":
    print("🚦 Initiating Integration Test for Upgraded Agent 2...")

    # Change "Bab-el-Mandeb" to "Strait of Hormuz" or "Strait of Malacca"
    mock_agent_1_output = {
    "geopolitical_event": "Tensions rising near the Strait of Hormuz.",
    "risk_score": 0.85,
    "target_region": "Persian Gulf",
    "strait_at_risk": "Strait of Hormuz" # 👈 Change this
    }   

    final_analysis = run_shipping_agent(mock_agent_1_output)
    
    print("\n================ FINAL UPGRADED GEMINI OUTPUT ================")
    print(final_analysis)
    print("==============================================================\n")