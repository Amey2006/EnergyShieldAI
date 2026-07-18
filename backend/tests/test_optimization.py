import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base, Supplier, IndianPort, Refinery, Tanker, PortRefineryLink
from backend.app.agents.port_intelligence import PortIntelligenceAgent
from backend.app.agents.refinery_compatibility import RefineryCompatibilityAgent
from backend.app.agents.port_to_refinery import PortToRefineryAgent
from backend.app.graph_engine import SupplyChainGraph

class TestLogisticsOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite database for test execution isolated from dev database
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)
        
        # Populate in-memory database with standard test scenarios
        db = cls.SessionLocal()
        
        # 1. Supplier
        cls.saudi = Supplier(
            name="Saudi Arabia", export_port="Ras Tanura", export_capacity_mbd=6.5,
            base_political_risk=30, preferred_crude_type="medium sour",
            api_gravity=34.0, sulfur_content=2.0, lat=26.6, lng=50.1
        )
        db.add(cls.saudi)
        
        # 2. Port
        cls.mundra = IndianPort(
            name="Mundra", throughput_capacity_mtpa=120.0,
            active_vessels=5, waiting_vessels=2, avg_waiting_hours=12.0,
            berth_utilization=0.65, historical_delay_hours=4.0, lat=22.7, lng=69.7
        )
        db.add(cls.mundra)
        
        # 3. Refinery
        cls.jamnagar = Refinery(
            name="Jamnagar", location="Gujarat", capacity_kbpd=1240.0,
            preferred_crude_type="medium sour", min_api=28.0, max_sulfur=3.0, lat=22.4, lng=70.0
        )
        db.add(cls.jamnagar)
        
        # 4. Inland route link
        cls.link = PortRefineryLink(
            port_name="Mundra", refinery_name="Jamnagar", distance_km=80.0,
            pipeline_available=True, rail_available=True, cost_per_barrel=0.4,
            storage_available_mb=5.0
        )
        db.add(cls.link)
        
        db.commit()
        db.close()

    def test_port_congestion_formula(self):
        db = self.SessionLocal()
        agent = PortIntelligenceAgent()
        analysis = agent.analyze_port(db, "Mundra")
        
        # Congestion Score = (Vessel Score * 0.3 + Time Score * 0.3 + Berth Util * 0.2 + Delay * 0.2)
        # Waiting vessels = 2 -> score = (2/20)*100 = 10
        # Avg waiting hours = 12 -> score = (12/72)*100 = 16.66
        # Berth util = 0.65 -> score = 65
        # Hist delay = 4 -> score = (4/24)*100 = 16.66
        # Congestion = 10*0.3 + 16.66*0.3 + 65*0.2 + 16.66*0.2 = 3 + 5 + 13 + 3.33 = 24.33
        
        self.assertEqual(analysis["port"], "Mundra")
        self.assertAlmostEqual(analysis["congestion_score"], 24.3, places=1)
        self.assertEqual(analysis["risk_level"], "low")
        db.close()

    def test_refinery_compatibility_scoring(self):
        db = self.SessionLocal()
        agent = RefineryCompatibilityAgent()
        analysis = agent.check_compatibility(db, "Saudi Arabia", "Jamnagar")
        
        # Saudi API = 34, Jamnagar min API = 28 -> compatible
        # Saudi Sulfur = 2%, Jamnagar max Sulfur = 3% -> compatible
        # Supplier Crude = "medium sour", Refinery crude = "medium sour" -> matched
        # Explicit Jamnagar override score = 94%
        
        self.assertEqual(analysis["compatibility_score"], 94.0)
        self.assertEqual(analysis["status"], "highly compatible")
        db.close()

    def test_port_to_refinery_inland_link(self):
        db = self.SessionLocal()
        agent = PortToRefineryAgent()
        analysis = agent.analyze_link(db, "Mundra", "Jamnagar")
        
        # Mundra -> Jamnagar score has explicit override = 95.0
        self.assertEqual(analysis["inland_score"], 95.0)
        self.assertEqual(analysis["primary_mode"], "Direct Pipeline")
        db.close()

    def test_graph_routing_dijkstra_normal_operations(self):
        graph = SupplyChainGraph()
        # Normal routing Basra Oil Terminal to Mundra
        route = graph.dijkstra_routing("Basra Oil Terminal", "Mundra")
        
        self.assertIsNotNone(route)
        self.assertIn("Strait of Hormuz", route["path"])
        self.assertIn("Arabian Sea", route["path"])
        self.assertLess(route["route_risk"], 80)
        
    def test_graph_routing_dijkstra_blockage_reroute(self):
        graph = SupplyChainGraph()
        
        # Route from Ras Tanura to Mundra, but block Strait of Hormuz
        # Standard route goes: Ras Tanura -> Strait of Hormuz -> Fujairah -> Arabian Sea -> Mundra
        # Bypassed route should use Saudi East-West pipeline to Red Sea!
        # Path: Ras Tanura -> Red Sea -> Bab el-Mandeb -> Arabian Sea -> Mundra
        route_normal = graph.dijkstra_routing("Ras Tanura", "Mundra")
        route_blocked = graph.dijkstra_routing("Ras Tanura", "Mundra", blocked_nodes=["Strait of Hormuz"])
        
        self.assertIsNotNone(route_normal)
        self.assertIsNotNone(route_blocked)
        self.assertIn("Strait of Hormuz", route_normal["path"])
        self.assertNotIn("Strait of Hormuz", route_blocked["path"])
        self.assertIn("Red Sea", route_blocked["path"])
        self.assertIn("Bab el-Mandeb", route_blocked["path"])
        self.assertGreater(route_blocked["route_risk"], route_normal["route_risk"])
        self.assertGreater(route_blocked["score"], route_normal["score"])

if __name__ == "__main__":
    unittest.main()
