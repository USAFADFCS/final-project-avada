import json
import requests
from fairlib.core.interfaces.tools import AbstractTool

AIRPORT_COORDS = {
    "DEN": {"lat": 39.8561, "lon": -104.6737},
    "MIA": {"lat": 25.7959, "lon": -80.2871},
    "DFW": {"lat": 32.8998, "lon": -97.0403},
    "LAX": {"lat": 33.9416, "lon": -118.4085},
    "JFK": {"lat": 40.6413, "lon": -73.7781},
    "ATL": {"lat": 33.6407, "lon": -84.4277},
}

class FlightSearchTool(AbstractTool):

    name = "flight_search"
    description = (
        "Returns real currently-airborne flights near origin and destination airports "
        "using the OpenSky API. No API key required."
    )

    def _box(self, iata):
        if iata not in AIRPORT_COORDS:
            return None
        lat = AIRPORT_COORDS[iata]["lat"]
        lon = AIRPORT_COORDS[iata]["lon"]
        return {
            "lamin": lat - 1.5,
            "lamax": lat + 1.5,
            "lomin": lon - 1.5,
            "lomax": lon + 1.5,
        }

    def _fetch_states(self, box):
        url = "https://opensky-network.org/api/states/all"
        try:
            return requests.get(url, params=box, timeout=10).json().get("states", [])
        except:
            return []

    def use(self, tool_input: str) -> str:
        try:
            data = json.loads(tool_input)
        except:
            return json.dumps({"error": "Invalid JSON input"})

        origin = data.get("origin")
        dest = data.get("destination")

        if not origin or not dest:
            return json.dumps({"error": "origin and destination required"})

        origin_box = self._box(origin)
        dest_box = self._box(dest)

        if not origin_box or not dest_box:
            return json.dumps({"error": "Unsupported IATA code"})

        # Fetch real flight states
        origin_flights = self._fetch_states(origin_box)
        dest_flights = self._fetch_states(dest_box)

        # Format flights near origin/dest
        def fmt(f):
            return {
                "icao24": f[0],
                "callsign": f[1].strip() if f[1] else None,
                "country": f[2],
                "altitude": f[13],
                "velocity_mps": f[9],
                "heading_deg": f[10],
            }

        origin_list = [fmt(f) for f in origin_flights]
        dest_list = [fmt(f) for f in dest_flights]

        return json.dumps({
            "origin_airport": origin,
            "destination_airport": dest,
            "flights_near_origin": origin_list[:10],
            "flights_near_destination": dest_list[:10],
            "note": "These are real aircraft currently near each airport (OpenSky live data).",
        }, indent=2)
