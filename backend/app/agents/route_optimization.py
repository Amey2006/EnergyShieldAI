from ..graph_engine import SupplyChainGraph
from .weather_risk import WeatherRiskAgent

class RouteOptimizationAgent:
    def __init__(self):
        self.name = "Route Optimization Agent"
        self.graph = SupplyChainGraph()
        self.weather_agent = WeatherRiskAgent()

    def optimize_route(self, supplier_port: str, destination_port: str, blocked_nodes: list = None) -> dict:
        """
        Calculates the optimal shipping pathway using graph-based Dijkstra's optimization.
        Incorporates live weather checks along path checkpoints.
        """
        # Resolve blocked nodes
        if blocked_nodes is None:
            blocked_nodes = []

        # Run Dijkstra routing
        route = self.graph.dijkstra_routing(
            start=supplier_port, 
            end=destination_port, 
            blocked_nodes=blocked_nodes
        )

        if not route:
            return {
                "agent": self.name,
                "status": "error",
                "message": f"No feasible shipping route found from '{supplier_port}' to '{destination_port}' under active blockages.",
                "logs": [f"Routing engine failed. '{supplier_port}' to '{destination_port}' is physically blocked by active alerts."]
            }

        # Analyze weather risks at each point in the route
        weather_reports = []
        highest_weather_risk = 0.0
        
        for node_name in route["path"]:
            node_info = self.graph.nodes.get(node_name)
            if node_info:
                # We can check weather for sea checkpoints and sea zones
                if node_info["type"] in ["checkpoint", "sea_zone"]:
                    weather = self.weather_agent.fetch_marine_weather(
                        lat=node_info["lat"],
                        lng=node_info["lng"],
                        location_name=node_name
                    )
                    weather_reports.append(weather)
                    highest_weather_risk = max(highest_weather_risk, weather["weather_risk_score"])

        # Compile final route scoring
        path_str = " → ".join(route["path"])
        
        return {
            "agent": self.name,
            "path": route["path"],
            "path_display": path_str,
            "distance_nm": route["distance"],
            "transit_days": route["time_days"],
            "shipping_cost_per_barrel": route["cost_per_barrel"],
            "base_route_risk": route["route_risk"],
            "highest_weather_risk_score": highest_weather_risk,
            "weather_reports": weather_reports,
            "logs": [
                f"Initializing route optimization solver from {supplier_port} to {destination_port}.",
                f"Resolved optimal shipping path: {path_str}.",
                f"Distance: {route['distance']} nautical miles. Est transit: {route['time_days']} days.",
                f"Average base shipping charter cost: ${route['cost_per_barrel']:.2f}/bbl.",
                f"Completed live weather safety audits at {len(weather_reports)} checkpoints along path.",
                f"Highest weather risk detected on route: {highest_weather_risk}/100."
            ]
        }
