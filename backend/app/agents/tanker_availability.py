from sqlalchemy.orm import Session
from ..models import Tanker
import math

class TankerAvailabilityAgent:
    def __init__(self):
        self.name = "Tanker Availability Agent"

    def check_tankers(self, db: Session, supplier_country: str, required_volume: float, deadline_days: float) -> dict:
        """
        Determines if there is enough shipping capacity (VLCC, Suezmax, Aframax) to meet the procurement volume.
        Calculates charter cost, ETA, and returns availability status.
        Reject routes where tanker arrival exceeds the disruption deadline.
        """
        # Get all active, available tankers
        available_tankers = db.query(Tanker).filter(Tanker.is_available == True).all()

        if not available_tankers:
            return {
                "agent": self.name,
                "VLCC_available": False,
                "available_count": 0,
                "eta_days": 99,
                "status": "rejected",
                "message": "No tankers are currently available in the charter market.",
                "logs": ["No available tankers found in DB registry. Route immediately disqualified."]
            }

        # Select the best tankers for our required volume
        # Classify tankers by size/cost efficiency
        # Rank by ETA (closest to supplier region)
        # We can assume a base travel time from tanker's current position to supplier country
        # For simplicity, we use the tanker's internal eta_days (seeded database attribute)
        # modified by a small randomized factor to represent real-time updates.
        
        # Sort tankers by ETA
        sorted_tankers = sorted(available_tankers, key=lambda t: t.eta_days)

        selected_tankers = []
        accumulated_capacity = 0.0
        total_charter_cost = 0.0
        max_eta = 0
        
        for tanker in sorted_tankers:
            if accumulated_capacity >= required_volume:
                break
            selected_tankers.append(tanker)
            accumulated_capacity += tanker.capacity_barrels
            total_charter_cost += tanker.charter_rate_per_day * tanker.eta_days
            max_eta = max(max_eta, tanker.eta_days)

        # Check if we can satisfy the volume
        if accumulated_capacity < required_volume:
            return {
                "agent": self.name,
                "VLCC_available": False,
                "available_count": len(available_tankers),
                "eta_days": max_eta,
                "status": "rejected",
                "message": f"Insufficient tanker capacity. Sourced only {accumulated_capacity/1e6}M bbls vs {required_volume/1e6}M bbls required.",
                "logs": [
                    f"Required: {required_volume/1e6}M barrels. Total available charter capacity is only {accumulated_capacity/1e6}M barrels.",
                    "Disqualifying route due to insufficient global tanker capacity."
                ]
            }

        # Check if ETA exceeds the deadline
        if max_eta > deadline_days:
            return {
                "agent": self.name,
                "VLCC_available": any(t.tanker_class == "VLCC" for t in selected_tankers),
                "available_count": len(selected_tankers),
                "eta_days": max_eta,
                "status": "rejected",
                "message": f"Closest tanker ETA is {max_eta} days, which exceeds deadline of {deadline_days} days.",
                "logs": [
                    f"Selected tankers: {', '.join([t.name for t in selected_tankers])}.",
                    f"Max ETA to origin: {max_eta} days exceeds deadline: {deadline_days} days.",
                    "Disqualifying route due to timeline violation."
                ]
            }

        return {
            "agent": self.name,
            "VLCC_available": any(t.tanker_class == "VLCC" for t in selected_tankers),
            "available_count": len(selected_tankers),
            "selected_tankers": [
                {
                    "name": t.name,
                    "class": t.tanker_class,
                    "capacity_barrels": t.capacity_barrels,
                    "charter_rate": t.charter_rate_per_day,
                    "eta_to_origin": f"{t.eta_days} days"
                } for t in selected_tankers
            ],
            "eta_days": max_eta,
            "total_charter_cost": total_charter_cost,
            "status": "approved",
            "logs": [
                f"Checking charter market for volume: {required_volume/1e6}M bbls.",
                f"Sourced {len(selected_tankers)} tankers totaling {accumulated_capacity/1e6}M bbls capacity.",
                f"Selected: {', '.join([t.name + ' (' + t.tanker_class + ')' for t in selected_tankers])}.",
                f"Combined fleet ETA to loading terminal: {max_eta} days (Deadline: {deadline_days} days).",
                f"Charter validation: APPROVED. Total initial charter fee: ${total_charter_cost:,.2f}."
            ]
        }
