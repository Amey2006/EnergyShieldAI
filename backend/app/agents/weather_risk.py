import requests
import random

class WeatherRiskAgent:
    def __init__(self):
        self.name = "Weather Risk Agent"
        self.weather_cache = {}

    def clear_cache(self):
        self.weather_cache = {}

    def fetch_marine_weather(self, lat: float, lng: float, location_name: str) -> dict:
        """
        Attempts to fetch live marine weather from Open-Meteo API.
        Falls back to geographically seeded mock weather on error/timeout.
        Caches results in memory to speed up multi-path optimization loops.
        """
        if location_name in self.weather_cache:
            return self.weather_cache[location_name]

        wind_speed_kmh = 15.0
        wave_height_m = 1.2
        storm_probability = 10.0
        visibility_km = 10.0
        source = "Geographical Seeded Model"

        # Try live Open-Meteo Marine/Forecast API
        try:
            # We fetch current wind speed and wave height if available
            # To handle both land and sea coordinates safely, we request wave_height from marine-api,
            # and wind_speed from standard forecast API.
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=wind_speed_10m&timezone=auto"
            response = requests.get(url, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                wind_speed_kmh = current.get("wind_speed_10m", 15.0)
                source = "Open-Meteo API"
                
                # Check marine API for wave height
                marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lng}&current=wave_height"
                marine_resp = requests.get(marine_url, timeout=2.0)
                if marine_resp.status_code == 200:
                    marine_data = marine_resp.json()
                    wave_height_m = marine_data.get("current", {}).get("wave_height", 1.2)
                    if wave_height_m is None:
                        wave_height_m = 1.2
        except Exception as e:
            # Silence error and use mock fallback (designed below)
            pass

        # Geographically realistic seeding adjustments for mock context
        # e.g., Arabian Sea during monsoon, or Cape of Good Hope having rough seas
        if "arabian sea" in location_name.lower():
            wave_height_m = max(wave_height_m, 2.0)
            wind_speed_kmh = max(wind_speed_kmh, 25.0)
        elif "cape of good hope" in location_name.lower():
            wave_height_m = max(wave_height_m, 3.5)
            wind_speed_kmh = max(wind_speed_kmh, 30.0)
            storm_probability = max(storm_probability, 25.0)
        elif "strait of hormuz" in location_name.lower():
            wave_height_m = min(wave_height_m, 1.5) # generally sheltered gulf
            wind_speed_kmh = min(wind_speed_kmh, 20.0)

        # Apply simulation offsets if active in system (will be passed or calculated)
        # Calculate Weather Risk Score (0 - 100)
        # 1. Wind speed risk: 50 km/h is 100% risk
        wind_risk = min(100.0, (wind_speed_kmh / 50.0) * 100.0)
        # 2. Wave height risk: 6 meters is 100% risk
        wave_risk = min(100.0, (wave_height_m / 6.0) * 100.0)
        # 3. Storm probability risk
        storm_risk = storm_probability

        weather_risk_score = (wind_risk * 0.3) + (wave_risk * 0.4) + (storm_risk * 0.3)
        weather_risk_score = round(weather_risk_score, 1)

        if weather_risk_score < 30:
            risk_level = "low"
        elif weather_risk_score < 60:
            risk_level = "medium"
        else:
            risk_level = "high"

        result = {
            "agent": self.name,
            "location": location_name,
            "coordinates": {"lat": lat, "lng": lng},
            "wind_speed": f"{round(wind_speed_kmh, 1)} km/h",
            "wave_height": f"{round(wave_height_m, 1)}m",
            "storm_probability": f"{int(storm_probability)}%",
            "weather_risk_score": weather_risk_score,
            "risk_level": risk_level,
            "data_source": source,
            "logs": [
                f"Assessing marine weather conditions at {location_name} ({lat}, {lng}).",
                f"Retrieved data via {source}.",
                f"Wind speed: {round(wind_speed_kmh, 1)} km/h, Wave height: {round(wave_height_m, 1)}m.",
                f"Calculated Weather Risk Score: {weather_risk_score}/100 ({risk_level} risk)."
            ]
        }
        self.weather_cache[location_name] = result
        return result
