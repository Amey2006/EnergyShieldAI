from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., "Saudi Arabia"
    export_port = Column(String) # e.g., "Ras Tanura"
    export_capacity_mbd = Column(Float) # Million barrels per day
    base_political_risk = Column(Float) # 0 to 100
    preferred_crude_type = Column(String) # e.g., "medium sour"
    api_gravity = Column(Float)
    sulfur_content = Column(Float)
    lat = Column(Float)
    lng = Column(Float)

class IndianPort(Base):
    __tablename__ = 'indian_ports'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., "Mundra"
    throughput_capacity_mtpa = Column(Float) # Million tonnes per annum
    active_vessels = Column(Integer, default=0)
    waiting_vessels = Column(Integer, default=0)
    avg_waiting_hours = Column(Float, default=12.0)
    berth_utilization = Column(Float, default=0.6) # 0.0 to 1.0
    historical_delay_hours = Column(Float, default=6.0)
    lat = Column(Float)
    lng = Column(Float)

class Refinery(Base):
    __tablename__ = 'refineries'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., "Jamnagar"
    location = Column(String)
    capacity_kbpd = Column(Float) # Thousand barrels per day
    preferred_crude_type = Column(String) # e.g., "medium sour"
    min_api = Column(Float)
    max_sulfur = Column(Float)
    lat = Column(Float)
    lng = Column(Float)

class Tanker(Base):
    __tablename__ = 'tankers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., "Ocean Giant"
    tanker_class = Column(String) # VLCC, Suezmax, Aframax
    capacity_barrels = Column(Float) # in barrels
    lat = Column(Float)
    lng = Column(Float)
    is_available = Column(Boolean, default=True)
    eta_days = Column(Integer, default=5)
    charter_rate_per_day = Column(Float) # in USD

class PortRefineryLink(Base):
    __tablename__ = 'port_refinery_links'
    
    id = Column(Integer, primary_key=True, index=True)
    port_name = Column(String, index=True)
    refinery_name = Column(String, index=True)
    distance_km = Column(Float)
    pipeline_available = Column(Boolean, default=True)
    rail_available = Column(Boolean, default=True)
    cost_per_barrel = Column(Float) # pipeline/rail cost per barrel in USD
    storage_available_mb = Column(Float) # Million barrels available capacity at connection
