from sqlalchemy.orm import Session
from ..models import IndianPort

class PortIntelligenceAgent:
    def __init__(self):
        self.name = "Port Intelligence Agent"

    def analyze_port(self, db: Session, port_name: str) -> dict:
        """
        Queries database for port characteristics and computes Congestion Score:
        Congestion Score = (Waiting Vessel Score * 0.3 + Waiting Time Score * 0.3 + Berth Utilization * 0.2 + Historical Delay * 0.2)
        """
        port = db.query(IndianPort).filter(IndianPort.name == port_name).first()
        if not port:
            return {
                "agent": self.name,
                "port": port_name,
                "status": "error",
                "message": f"Port '{port_name}' not found in database."
            }

        # Calculate normalized component scores (0 - 100)
        # 1. Waiting Vessel Score: Assume 20+ vessels is 100% capacity
        waiting_vessel_score = min(100.0, (port.waiting_vessels / 20.0) * 100.0)
        
        # 2. Waiting Time Score: Assume 72 hours is 100%
        waiting_time_score = min(100.0, (port.avg_waiting_hours / 72.0) * 100.0)
        
        # 3. Berth Utilization Score: Percentage value (0 - 100)
        berth_utilization_score = port.berth_utilization * 100.0
        
        # 4. Historical Delay Score: Assume 24 hours is 100%
        historical_delay_score = min(100.0, (port.historical_delay_hours / 24.0) * 100.0)

        # Weighted calculation
        congestion_score = (
            waiting_vessel_score * 0.3 +
            waiting_time_score * 0.3 +
            berth_utilization_score * 0.2 +
            historical_delay_score * 0.2
        )
        
        congestion_score = round(congestion_score, 1)

        # Determine overall port risk level
        if congestion_score < 30:
            risk_level = "low"
        elif congestion_score < 60:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "agent": self.name,
            "port": port.name,
            "congestion_score": congestion_score,
            "waiting_vessels": port.waiting_vessels,
            "waiting_time": f"{port.avg_waiting_hours} hours",
            "berth_utilization": f"{int(port.berth_utilization * 100)}%",
            "throughput_capacity_mtpa": port.throughput_capacity_mtpa,
            "risk_level": risk_level,
            "logs": [
                f"Analyzing port logistics at {port.name}.",
                f"Queue metrics: {port.waiting_vessels} vessels waiting, avg time {port.avg_waiting_hours} hrs.",
                f"Berth utilization sits at {int(port.berth_utilization * 100)}%.",
                f"Calculated Port Congestion Score: {congestion_score}/100 ({risk_level} risk)."
            ]
        }
