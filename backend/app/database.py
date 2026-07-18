import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Supplier, IndianPort, Refinery, Tanker, PortRefineryLink

# Toggle database connection based on environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./energy_resilience.db")

# SQLite fallback config (check if it's SQLite to add specific arguments)
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_data()

def seed_data():
    db = SessionLocal()
    try:
        # Check if database is already seeded
        if db.query(Supplier).first() is not None:
            return
        
        print("Seeding database with realistic crude supply chain configurations...")
        
        # 1. Suppliers
        suppliers = [
            Supplier(name="Saudi Arabia", export_port="Ras Tanura", export_capacity_mbd=6.5, base_political_risk=30, preferred_crude_type="medium sour", api_gravity=34.0, sulfur_content=2.0, lat=26.6375, lng=50.1694),
            Supplier(name="UAE", export_port="Fujairah", export_capacity_mbd=3.0, base_political_risk=15, preferred_crude_type="light sweet", api_gravity=40.0, sulfur_content=0.8, lat=25.1164, lng=56.3681),
            Supplier(name="Iraq", export_port="Basra Oil Terminal", export_capacity_mbd=3.8, base_political_risk=55, preferred_crude_type="heavy sour", api_gravity=29.5, sulfur_content=2.9, lat=29.7892, lng=48.7903),
            Supplier(name="USA", export_port="Houston Port", export_capacity_mbd=4.0, base_political_risk=5, preferred_crude_type="light sweet", api_gravity=44.0, sulfur_content=0.15, lat=29.7604, lng=-95.3698),
            Supplier(name="Brazil", export_port="Port of Santos", export_capacity_mbd=1.8, base_political_risk=20, preferred_crude_type="medium sweet", api_gravity=31.0, sulfur_content=0.5, lat=-23.9608, lng=-46.3336),
            Supplier(name="Nigeria", export_port="Port Harcourt", export_capacity_mbd=1.5, base_political_risk=50, preferred_crude_type="light sweet", api_gravity=37.0, sulfur_content=0.14, lat=4.7758, lng=7.0094),
            Supplier(name="Russia", export_port="Novorossiysk", export_capacity_mbd=2.5, base_political_risk=75, preferred_crude_type="medium sour", api_gravity=32.0, sulfur_content=1.8, lat=44.7244, lng=37.7675)
        ]
        db.add_all(suppliers)
        
        # 2. Indian Ports
        ports = [
            IndianPort(name="Mundra", throughput_capacity_mtpa=120.0, active_vessels=5, waiting_vessels=2, avg_waiting_hours=12.0, berth_utilization=0.65, historical_delay_hours=4.0, lat=22.7381, lng=69.7042),
            IndianPort(name="Mumbai", throughput_capacity_mtpa=80.0, active_vessels=8, waiting_vessels=6, avg_waiting_hours=36.0, berth_utilization=0.85, historical_delay_hours=18.0, lat=18.9500, lng=72.8500),
            IndianPort(name="Kochi", throughput_capacity_mtpa=60.0, active_vessels=3, waiting_vessels=1, avg_waiting_hours=10.0, berth_utilization=0.50, historical_delay_hours=2.0, lat=9.9667, lng=76.2667),
            IndianPort(name="Paradip", throughput_capacity_mtpa=150.0, active_vessels=6, waiting_vessels=3, avg_waiting_hours=20.0, berth_utilization=0.72, historical_delay_hours=8.0, lat=20.2600, lng=86.6800),
            IndianPort(name="Visakhapatnam", throughput_capacity_mtpa=70.0, active_vessels=4, waiting_vessels=2, avg_waiting_hours=16.0, berth_utilization=0.58, historical_delay_hours=5.0, lat=17.6833, lng=83.2833),
            IndianPort(name="Chennai", throughput_capacity_mtpa=50.0, active_vessels=3, waiting_vessels=1, avg_waiting_hours=14.0, berth_utilization=0.52, historical_delay_hours=3.5, lat=13.0827, lng=80.2707)
        ]
        db.add_all(ports)
        
        # 3. Refineries
        refineries = [
            Refinery(name="Jamnagar", location="Gujarat", capacity_kbpd=1240.0, preferred_crude_type="medium sour", min_api=28.0, max_sulfur=3.0, lat=22.4700, lng=70.0700),
            Refinery(name="Mumbai HPCL/BPCL", location="Maharashtra", capacity_kbpd=300.0, preferred_crude_type="light sweet", min_api=32.0, max_sulfur=1.5, lat=19.0100, lng=72.9100),
            Refinery(name="Paradip IOCL", location="Odisha", capacity_kbpd=300.0, preferred_crude_type="heavy sour", min_api=25.0, max_sulfur=3.5, lat=20.2700, lng=86.6700),
            Refinery(name="Kochi BPCL", location="Kerala", capacity_kbpd=310.0, preferred_crude_type="medium sour", min_api=28.0, max_sulfur=2.5, lat=9.9500, lng=76.3500),
            Refinery(name="Visakhapatnam HPCL", location="Andhra Pradesh", capacity_kbpd=166.0, preferred_crude_type="medium sour", min_api=28.0, max_sulfur=2.0, lat=17.7200, lng=83.2200),
            Refinery(name="Panipat IOCL", location="Haryana (Inland)", capacity_kbpd=300.0, preferred_crude_type="medium sour", min_api=30.0, max_sulfur=2.0, lat=29.3900, lng=76.9700),
            Refinery(name="Chennai CPCL", location="Tamil Nadu", capacity_kbpd=210.0, preferred_crude_type="medium sour", min_api=28.0, max_sulfur=2.2, lat=13.1600, lng=80.3000)
        ]
        db.add_all(refineries)
        
        # 4. Tankers
        tankers = [
            Tanker(name="Antigravity Pioneer", tanker_class="VLCC", capacity_barrels=2000000.0, lat=10.0, lng=60.0, is_available=True, eta_days=4, charter_rate_per_day=45000.0),
            Tanker(name="Oceanic Titan", tanker_class="VLCC", capacity_barrels=2000000.0, lat=24.0, lng=58.0, is_available=True, eta_days=2, charter_rate_per_day=48000.0),
            Tanker(name="Gulf Horizon", tanker_class="Suezmax", capacity_barrels=1000000.0, lat=12.0, lng=45.0, is_available=True, eta_days=6, charter_rate_per_day=32000.0),
            Tanker(name="Basra Voyager", tanker_class="Suezmax", capacity_barrels=1000000.0, lat=28.0, lng=49.0, is_available=False, eta_days=0, charter_rate_per_day=30000.0),
            Tanker(name="Atlantic Breeze", tanker_class="VLCC", capacity_barrels=2000000.0, lat=-15.0, lng=-20.0, is_available=True, eta_days=15, charter_rate_per_day=52000.0),
            Tanker(name="Red Sea Sentinel", tanker_class="Aframax", capacity_barrels=700000.0, lat=20.0, lng=38.0, is_available=True, eta_days=8, charter_rate_per_day=24000.0),
            Tanker(name="Pacific Energy", tanker_class="VLCC", capacity_barrels=2000000.0, lat=0.0, lng=95.0, is_available=True, eta_days=10, charter_rate_per_day=50000.0),
            Tanker(name="Siberian Quest", tanker_class="Aframax", capacity_barrels=700000.0, lat=40.0, lng=20.0, is_available=True, eta_days=11, charter_rate_per_day=28000.0),
            Tanker(name="Mumbai Crest", tanker_class="Aframax", capacity_barrels=700000.0, lat=18.5, lng=71.5, is_available=True, eta_days=1, charter_rate_per_day=22000.0),
            Tanker(name="Paradip Star", tanker_class="VLCC", capacity_barrels=2000000.0, lat=15.0, lng=85.0, is_available=True, eta_days=3, charter_rate_per_day=46000.0)
        ]
        db.add_all(tankers)
        
        # 5. Inland Connections (Port-to-Refinery Links)
        # Mundra Port connections
        links = [
            PortRefineryLink(port_name="Mundra", refinery_name="Jamnagar", distance_km=80.0, pipeline_available=True, rail_available=True, cost_per_barrel=0.4, storage_available_mb=5.0),
            PortRefineryLink(port_name="Mundra", refinery_name="Panipat IOCL", distance_km=1100.0, pipeline_available=True, rail_available=True, cost_per_barrel=2.2, storage_available_mb=4.0),
            PortRefineryLink(port_name="Mundra", refinery_name="Mumbai HPCL/BPCL", distance_km=850.0, pipeline_available=False, rail_available=True, cost_per_barrel=3.5, storage_available_mb=1.5),
            
            # Mumbai Port connections
            PortRefineryLink(port_name="Mumbai", refinery_name="Mumbai HPCL/BPCL", distance_km=15.0, pipeline_available=True, rail_available=True, cost_per_barrel=0.1, storage_available_mb=3.0),
            PortRefineryLink(port_name="Mumbai", refinery_name="Jamnagar", distance_km=800.0, pipeline_available=False, rail_available=True, cost_per_barrel=3.2, storage_available_mb=2.0),
            
            # Kochi Port connections
            PortRefineryLink(port_name="Kochi", refinery_name="Kochi BPCL", distance_km=20.0, pipeline_available=True, rail_available=True, cost_per_barrel=0.15, storage_available_mb=2.5),
            
            # Paradip Port connections
            PortRefineryLink(port_name="Paradip", refinery_name="Paradip IOCL", distance_km=15.0, pipeline_available=True, rail_available=True, cost_per_barrel=0.1, storage_available_mb=4.5),
            PortRefineryLink(port_name="Paradip", refinery_name="Panipat IOCL", distance_km=1600.0, pipeline_available=False, rail_available=True, cost_per_barrel=4.8, storage_available_mb=1.0),
            
            # Visakhapatnam Port connections
            PortRefineryLink(port_name="Visakhapatnam", refinery_name="Visakhapatnam HPCL", distance_km=12.0, pipeline_available=True, rail_available=True, cost_per_barrel=0.1, storage_available_mb=2.0),
            
            # Chennai Port connections
            PortRefineryLink(port_name="Chennai", refinery_name="Chennai CPCL", distance_km=25.0, pipeline_available=True, rail_available=True, cost_per_barrel=0.2, storage_available_mb=2.2),
            PortRefineryLink(port_name="Chennai", refinery_name="Panipat IOCL", distance_km=2000.0, pipeline_available=False, rail_available=True, cost_per_barrel=5.5, storage_available_mb=1.0)
        ]
        db.add_all(links)
        
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()
