import heapq

class SupplyChainGraph:
    def __init__(self):
        # Dictionary of nodes with their details
        self.nodes = {}
        # Dictionary of adjacency list: {u: {v: {distance, time, cost, risk_factor}}}
        self.edges = {}
        self._initialize_graph()

    def _initialize_graph(self):
        # 1. Add Nodes
        # Format: self.add_node(name, type, lat, lng, base_risk)
        # Origins (Supplier Ports)
        self.add_node("Basra Oil Terminal", "origin_port", 29.7892, 48.7903, 20)
        self.add_node("Ras Tanura", "origin_port", 26.6375, 50.1694, 15)
        self.add_node("Fujairah", "origin_port", 25.1164, 56.3681, 10)
        self.add_node("Houston Port", "origin_port", 29.7604, -95.3698, 5)
        self.add_node("Port of Santos", "origin_port", -23.9608, -46.3336, 10)
        self.add_node("Port Harcourt", "origin_port", 4.7758, 7.0094, 25)
        self.add_node("Novorossiysk", "origin_port", 44.7244, 37.7675, 30)

        # Shipping Checkpoints & Transit Channels
        self.add_node("Strait of Hormuz", "checkpoint", 26.5667, 56.2500, 40)
        self.add_node("Bab el-Mandeb", "checkpoint", 12.5833, 43.3333, 45)
        self.add_node("Suez Canal", "checkpoint", 29.9292, 32.5514, 25)
        self.add_node("Red Sea", "checkpoint", 20.0000, 38.0000, 35)
        self.add_node("Cape of Good Hope", "checkpoint", -34.3568, 18.4967, 5)
        self.add_node("Malacca Strait", "checkpoint", 1.4333, 102.9333, 15)
        self.add_node("Atlantic Ocean", "sea_zone", 10.0000, -30.0000, 5)
        self.add_node("Black Sea", "sea_zone", 43.0000, 34.0000, 25)
        self.add_node("Arabian Sea", "sea_zone", 15.0000, 65.0000, 10)
        self.add_node("Indian Ocean", "sea_zone", -5.0000, 75.0000, 5)
        self.add_node("Bay of Bengal", "sea_zone", 15.0000, 88.0000, 10)

        # Indian Ports (Destinations)
        self.add_node("Mundra", "destination_port", 22.7381, 69.7042, 5)
        self.add_node("Mumbai", "destination_port", 18.9500, 72.8500, 5)
        self.add_node("Kochi", "destination_port", 9.9667, 76.2667, 5)
        self.add_node("Paradip", "destination_port", 20.2600, 86.6800, 5)
        self.add_node("Visakhapatnam", "destination_port", 17.6833, 83.2833, 5)
        self.add_node("Chennai", "destination_port", 13.0827, 80.2707, 5)

        # 2. Add Edges (u, v, distance_nautical_miles, base_time_days, base_cost_per_barrel, risk_multiplier)
        # Persian Gulf Routes
        self.add_edge("Basra Oil Terminal", "Strait of Hormuz", 350, 1.0, 0.40, 1.2)
        self.add_edge("Ras Tanura", "Strait of Hormuz", 180, 0.5, 0.20, 1.0)
        self.add_edge("Strait of Hormuz", "Fujairah", 90, 0.3, 0.15, 1.1)
        self.add_edge("Fujairah", "Arabian Sea", 200, 0.6, 0.20, 1.0)
        self.add_edge("Strait of Hormuz", "Arabian Sea", 280, 0.8, 0.30, 1.2)
        
        # Saudi Bypass Route (East-West Pipeline to Red Sea)
        self.add_edge("Ras Tanura", "Red Sea", 750, 1.5, 0.90, 1.0) # Pipeline land transport cost
        self.add_edge("Red Sea", "Bab el-Mandeb", 620, 1.6, 0.30, 1.3)

        # Red Sea / Bab el-Mandeb to Arabian Sea
        self.add_edge("Bab el-Mandeb", "Arabian Sea", 600, 1.5, 0.30, 1.4)
        
        # Suez Routes (Suez connects Red Sea to Mediterranean/Atlantic/Black Sea)
        self.add_edge("Red Sea", "Suez Canal", 800, 2.0, 0.45, 1.1)
        self.add_edge("Suez Canal", "Black Sea", 750, 2.2, 0.50, 1.2)
        self.add_edge("Suez Canal", "Atlantic Ocean", 1900, 5.0, 1.10, 1.0)
        
        # Black Sea Routes (Russia)
        self.add_edge("Novorossiysk", "Black Sea", 50, 0.2, 0.10, 1.5)
        self.add_edge("Black Sea", "Suez Canal", 800, 2.3, 0.60, 1.3)

        # West Africa (Nigeria) Routes
        self.add_edge("Port Harcourt", "Atlantic Ocean", 150, 0.5, 0.25, 1.2)
        self.add_edge("Atlantic Ocean", "Cape of Good Hope", 3800, 10.0, 2.20, 1.0)
        
        # South America (Brazil) Routes
        self.add_edge("Port of Santos", "Atlantic Ocean", 100, 0.3, 0.20, 1.0)
        
        # US Gulf Coast (USA) Routes
        self.add_edge("Houston Port", "Atlantic Ocean", 600, 1.8, 0.45, 1.0)

        # Cape of Good Hope to Indian Ocean
        self.add_edge("Cape of Good Hope", "Indian Ocean", 4200, 11.5, 2.50, 1.0)
        self.add_edge("Atlantic Ocean", "Indian Ocean", 6500, 18.0, 3.80, 1.0) # Direct crossing
        
        # Ocean basins to Indian destinations
        self.add_edge("Arabian Sea", "Indian Ocean", 1200, 3.2, 0.70, 1.0)
        self.add_edge("Indian Ocean", "Bay of Bengal", 1000, 2.8, 0.60, 1.0)
        
        # Connect Arabian Sea to West Coast Indian Ports
        self.add_edge("Arabian Sea", "Mundra", 400, 1.2, 0.25, 1.0)
        self.add_edge("Arabian Sea", "Mumbai", 300, 1.0, 0.20, 1.0)
        self.add_edge("Arabian Sea", "Kochi", 650, 1.8, 0.35, 1.0)
        
        # Connect Indian Ocean / Bay of Bengal to East Coast Indian Ports
        self.add_edge("Indian Ocean", "Kochi", 500, 1.4, 0.30, 1.0)
        self.add_edge("Bay of Bengal", "Paradip", 350, 1.0, 0.22, 1.0)
        self.add_edge("Bay of Bengal", "Visakhapatnam", 250, 0.8, 0.18, 1.0)
        self.add_edge("Bay of Bengal", "Chennai", 300, 0.9, 0.20, 1.0)

    def add_node(self, name, node_type, lat, lng, base_risk):
        self.nodes[name] = {
            "name": name,
            "type": node_type,
            "lat": lat,
            "lng": lng,
            "base_risk": base_risk
        }
        if name not in self.edges:
            self.edges[name] = {}

    def add_edge(self, u, v, distance, time, cost, risk_mult):
        # Bidirectional for sea lanes, though we enforce flows from supplier to India in solver
        if u not in self.edges:
            self.edges[u] = {}
        if v not in self.edges:
            self.edges[v] = {}
            
        self.edges[u][v] = {
            "distance": distance,
            "time": time,
            "cost": cost,
            "risk_multiplier": risk_mult
        }
        self.edges[v][u] = {
            "distance": distance,
            "time": time,
            "cost": cost,
            "risk_multiplier": risk_mult
        }

    def get_route_details(self, path):
        total_distance = 0.0
        total_time = 0.0
        total_cost = 0.0
        max_segment_risk = 0.0
        path_nodes_risk = 0.0
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_data = self.edges[u][v]
            total_distance += edge_data["distance"]
            total_time += edge_data["time"]
            total_cost += edge_data["cost"]
            
            # Risk estimation based on checkpoint transit
            node_risk = self.nodes[v]["base_risk"]
            max_segment_risk = max(max_segment_risk, node_risk * edge_data["risk_multiplier"])
            path_nodes_risk += node_risk
            
        # Overall route risk normalized out of 100
        overall_risk_score = min(99.0, max_segment_risk * 1.2 + (path_nodes_risk / len(path)) * 0.4)
        return {
            "distance": round(total_distance, 1),
            "time_days": round(total_time, 1),
            "cost_per_barrel": round(total_cost, 2),
            "route_risk": round(overall_risk_score, 1)
        }

    def dijkstra_routing(self, start, end, blocked_nodes=None, weight_cost=1.0, weight_time=1.5, weight_risk=2.0):
        if blocked_nodes is None:
            blocked_nodes = set()
        else:
            blocked_nodes = set(blocked_nodes)

        if start in blocked_nodes or end in blocked_nodes:
            return None

        # heap queue: (accumulated_score, current_node, path)
        queue = [(0.0, start, [start])]
        visited = {}

        while queue:
            (cost, current, path) = heapq.heappop(queue)

            if current == end:
                route_metrics = self.get_route_details(path)
                return {
                    "path": path,
                    "score": cost,
                    **route_metrics
                }

            if current in visited and visited[current] <= cost:
                continue
            visited[current] = cost

            for neighbor, edge_data in self.edges[current].items():
                if neighbor in blocked_nodes:
                    continue

                # Calculate composite edge weight for minimization
                edge_dist = edge_data["distance"]
                edge_time = edge_data["time"]
                edge_cost = edge_data["cost"]
                edge_risk = self.nodes[neighbor]["base_risk"] * edge_data["risk_multiplier"]

                # Composite score to optimize
                edge_composite_score = (
                    (edge_cost * 15.0 * weight_cost) + 
                    (edge_time * 5.0 * weight_time) + 
                    (edge_risk * 0.8 * weight_risk)
                )

                new_cost = cost + edge_composite_score
                heapq.heappush(queue, (new_cost, neighbor, path + [neighbor]))

        return None
