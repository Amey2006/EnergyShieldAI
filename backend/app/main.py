import os
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .models import Supplier, IndianPort, Refinery, Tanker, PortRefineryLink
from .database import SessionLocal, init_db
from .agents.supervisor import EnergyLogisticsSupervisorAgent
from .vector_store import VectorStore

# In-memory system state for active blockages and disruptions
app_state = {
    "blocked_nodes": [],
    "active_disruptions": []
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables and seed data
    init_db()
    yield
    # Cleanup on shutdown

app = FastAPI(
    title="AI Energy Logistics Optimization Agent API",
    description="Module 2 API service for India's Crude Import Supply Chain Resilience Platform.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Instantiate global vector store and supervisor agent
vector_store = VectorStore()
supervisor_agent = EnergyLogisticsSupervisorAgent()

# ----------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------
class OptimizeRequest(BaseModel):
    event: Optional[str] = Field(default="Normal Operations")
    required_volume: str = Field(default="5 million barrels", description="e.g. '5 million barrels' or '5'")
    deadline: str = Field(default="15 days", description="e.g. '15 days' or '15'")
    preferred_crude: str = Field(default="medium sour crude")
    risk_level: str = Field(default="medium")
    target_refinery: Optional[str] = None
    blocked_nodes: Optional[List[str]] = None

class DisruptionRequest(BaseModel):
    scenario: str # e.g. "Strait of Hormuz partial blockage", "Arabian Sea Cyclone", "Clear Disruptions"
    details: Optional[str] = None

class VectorQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 2

# Helper function to parse volume & deadline text to numeric days/barrels
def parse_volume(vol_str: str) -> float:
    # Converts e.g. "5 million barrels" or "5M" or "5" to 5.0 (float)
    clean = vol_str.lower().replace("million", "").replace("barrels", "").replace("bbls", "").replace("m", "").strip()
    try:
        return float(clean)
    except ValueError:
        return 5.0 # fallback default

def parse_deadline(dead_str: str) -> float:
    # Converts e.g. "15 days" or "15" to 15.0
    clean = dead_str.lower().replace("days", "").replace("day", "").strip()
    try:
        return float(clean)
    except ValueError:
        return 15.0

# ----------------------------------------------------
# Endpoints
# ----------------------------------------------------
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "Energy Route AI Backend"}

@app.post("/api/optimize")
def optimize_logistics(req: OptimizeRequest, db: Session = Depends(get_db)):
    # Parse inputs
    volume_num = parse_volume(req.required_volume)
    deadline_num = parse_deadline(req.deadline)
    
    # Merge blockages from request and active system state
    req_blocked = req.blocked_nodes or []
    merged_blocked = list(set(req_blocked + app_state["blocked_nodes"]))

    input_params = {
        "required_volume": volume_num,
        "deadline": deadline_num,
        "preferred_crude": req.preferred_crude,
        "risk_level": req.risk_level,
        "blocked_nodes": merged_blocked,
        "target_refinery": req.target_refinery
    }

    try:
        result = supervisor_agent.run_optimization(db, input_params)
        
        # Include current blockage state in response
        result["active_blockages"] = merged_blocked
        result["active_disruptions"] = app_state["active_disruptions"]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulate-disruption")
def simulate_disruption(req: DisruptionRequest, db: Session = Depends(get_db)):
    scenario = req.scenario.lower()
    
    # Reset first if clear requested
    if "clear" in scenario:
        app_state["blocked_nodes"] = []
        app_state["active_disruptions"] = []
        
        # Restore port stats to default values
        db.query(IndianPort).update({
            IndianPort.waiting_vessels: 2, 
            IndianPort.avg_waiting_hours: 12.0,
            IndianPort.berth_utilization: 0.60
        })
        db.commit()
        return {"status": "success", "message": "All disruptions cleared. Reverting to normal operation.", "state": app_state}

    # Scenario: Strait of Hormuz blockage
    if "hormuz" in scenario:
        app_state["blocked_nodes"] = list(set(app_state["blocked_nodes"] + ["Strait of Hormuz"]))
        app_state["active_disruptions"].append({
            "name": "Strait of Hormuz Blockage",
            "type": "Geopolitical risk blockage",
            "impact": "Middle East Gulf exports (Basra, Ras Tanura) blocked from maritime transit. Re-routing required."
        })
        # Set high risk/impact of the blocked node
        message = "Strait of Hormuz is blocked. Basra and Ras Tanura maritime routes are disrupted."
        
    # Scenario: Arabian Sea cyclone
    elif "cyclone" in scenario or "weather" in scenario:
        # Cyclone blocks Arabian Sea transit & heavily impacts Mundra/Mumbai port congestion
        app_state["active_disruptions"].append({
            "name": "Arabian Sea Cyclone Alert",
            "type": "Weather event disruption",
            "impact": "Wave heights exceed 5.5m. Mundra and Mumbai ports experiencing berth shutdown."
        })
        
        # Increase port congestions dramatically
        mundra = db.query(IndianPort).filter(IndianPort.name == "Mundra").first()
        if mundra:
            mundra.waiting_vessels = 12
            mundra.avg_waiting_hours = 60.0
            mundra.berth_utilization = 0.95
            
        mumbai = db.query(IndianPort).filter(IndianPort.name == "Mumbai").first()
        if mumbai:
            mumbai.waiting_vessels = 18
            mumbai.avg_waiting_hours = 84.0
            mumbai.berth_utilization = 0.98

        db.commit()
        message = "Cyclone simulated in Arabian Sea. Wave heights increased. Mundra/Mumbai port waiting hours spiked."
    
    # Scenario: Mundra port congestion
    elif "mundra congestion" in scenario:
        app_state["active_disruptions"].append({
            "name": "Mundra Port Labour Strike",
            "type": "Operational congestion",
            "impact": "Berth utilization spiked to 98% with 15 waiting vessels."
        })
        mundra = db.query(IndianPort).filter(IndianPort.name == "Mundra").first()
        if mundra:
            mundra.waiting_vessels = 15
            mundra.avg_waiting_hours = 52.0
            mundra.berth_utilization = 0.98
        db.commit()
        message = "Mundra Port congestion simulated. Waiting times increased to 52 hours."

    else:
        message = f"Simulated custom event: {req.scenario}"
        app_state["active_disruptions"].append({
            "name": req.scenario,
            "type": "Custom disruption",
            "impact": req.details or "Unspecified impact parameters."
        })

    return {"status": "success", "message": message, "state": app_state}

@app.get("/api/digital-twin")
def get_digital_twin_layers(db: Session = Depends(get_db)):
    """
    Returns structured data detailing all nodes, edges, active tankers, and ports
    to lay out the Digital Twin Map on the frontend.
    """
    # Load all database elements
    suppliers = db.query(Supplier).all()
    ports = db.query(IndianPort).all()
    refineries = db.query(Refinery).all()
    tankers = db.query(Tanker).all()
    links = db.query(PortRefineryLink).all()

    # Load graph nodes & edges
    graph = supervisor_agent.route_agent.graph
    
    # Format graph nodes
    map_nodes = []
    for name, node in graph.nodes.items():
        # Match with database values if possible to show dynamic stats
        info = {}
        if node["type"] == "origin_port":
            supp = next((s for s in suppliers if s.export_port == name), None)
            if supp:
                info = {
                    "supplier": supp.name,
                    "crude_type": supp.preferred_crude_type,
                    "capacity_mbd": supp.export_capacity_mbd,
                    "political_risk": supp.base_political_risk
                }
        elif node["type"] == "destination_port":
            p = next((x for x in ports if x.name == name), None)
            if p:
                info = {
                    "waiting_vessels": p.waiting_vessels,
                    "avg_waiting": f"{p.avg_waiting_hours} hrs",
                    "utilization": f"{int(p.berth_utilization * 100)}%",
                    "capacity": f"{p.throughput_capacity_mtpa} MTPA"
                }
        elif node["type"] == "refinery":
            ref = next((r for r in refineries if r.name == name), None)
            if ref:
                info = {
                    "capacity_kbpd": ref.capacity_kbpd,
                    "crude_preferred": ref.preferred_crude_type
                }

        map_nodes.append({
            "name": name,
            "type": node["type"],
            "lat": node["lat"],
            "lng": node["lng"],
            "base_risk": node["base_risk"],
            "info": info
        })

    # Format graph edges
    map_edges = []
    for u, neighbors in graph.edges.items():
        for v, edge in neighbors.items():
            # Avoid duplicate listing for undirected representation
            if u < v:
                map_edges.append({
                    "from_node": u,
                    "to_node": v,
                    "from_coords": [graph.nodes[u]["lat"], graph.nodes[u]["lng"]],
                    "to_coords": [graph.nodes[v]["lat"], graph.nodes[v]["lng"]],
                    "distance_nm": edge["distance"],
                    "time_days": edge["time"],
                    "cost": edge["cost"],
                    "risk_multiplier": edge["risk_multiplier"]
                })

    # Inland connections
    inland_routes = []
    for link in links:
        p_node = graph.nodes.get(link.port_name)
        r_node = graph.nodes.get(link.refinery_name)
        if p_node and r_node:
            inland_routes.append({
                "port": link.port_name,
                "refinery": link.refinery_name,
                "port_coords": [p_node["lat"], p_node["lng"]],
                "refinery_coords": [r_node["lat"], r_node["lng"]],
                "distance_km": link.distance_km,
                "cost_per_barrel": link.cost_per_barrel,
                "pipeline_available": link.pipeline_available
            })

    # Active tankers
    active_tankers_list = []
    for t in tankers:
        active_tankers_list.append({
            "name": t.name,
            "class": t.tanker_class,
            "lat": t.lat,
            "lng": t.lng,
            "is_available": t.is_available,
            "eta_days": t.eta_days,
            "capacity": t.capacity_barrels
        })

    return {
        "nodes": map_nodes,
        "edges": map_edges,
        "inland_routes": inland_routes,
        "tankers": active_tankers_list,
        "blocked_nodes": app_state["blocked_nodes"],
        "active_disruptions": app_state["active_disruptions"]
    }

@app.post("/api/vector-search")
def search_resilience_docs(req: VectorQueryRequest):
    try:
        results = vector_store.search(req.query, req.top_k)
        return {
            "query": req.query,
            "results": [
                {
                    "id": r["document"]["id"],
                    "title": r["document"]["title"],
                    "content": r["document"]["content"],
                    "score": round(r["score"], 3)
                } for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
