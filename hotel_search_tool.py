import json
import requests
from fairlib.core.interfaces.tools import AbstractTool

# Same city → coordinates lookup used for restaurants + activities
CITY_COORDS = {
    "miami": (25.7617, -80.1918),
    "denver": (39.7392, -104.9903),
    "orlando": (28.5383, -81.3792),
    "los angeles": (34.0522, -118.2437),
    "new york": (40.7128, -74.0060),
    "chicago": (41.8781, -87.6298),
    "dallas": (32.7767, -96.7970),
}

class HotelSearchTool(AbstractTool):

    name = "hotel_search"
    description = (
        "Finds hotels, motels, guest houses, hostels, and lodging near a city "
        "using OpenStreetMap Overpass API. Requires 'city', optional 'radius_km'."
    )

    def _get_coords(self, city: str):
        city = city.lower()
        return CITY_COORDS.get(city)

    def _query_overpass(self, lat, lon, radius_km):
        radius_m = radius_km * 1000

        query = f"""
        [out:json];
        (
          node["tourism"="hotel"](around:{radius_m},{lat},{lon});
          node["tourism"="motel"](around:{radius_m},{lat},{lon});
          node["tourism"="hostel"](around:{radius_m},{lat},{lon});
          node["tourism"="guest_house"](around:{radius_m},{lat},{lon});
          node["amenity"="hotel"](around:{radius_m},{lat},{lon});
          node["amenity"="lodging"](around:{radius_m},{lat},{lon});
        );
        out;
        """

        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=25
        )

        return response.json()

    def use(self, tool_input: str) -> str:
        try:
            payload = json.loads(tool_input)
        except:
            return json.dumps({"error": "Invalid JSON input"})

        city = payload.get("city")
        radius_km = payload.get("radius_km", 4)

        if not city:
            return json.dumps({"error": "Missing required field: city"})

        coords = self._get_coords(city)
        if not coords:
            return json.dumps({"error": f"City '{city}' not supported."})

        lat, lon = coords

        try:
            data = self._query_overpass(lat, lon, radius_km)
        except Exception as e:
            return json.dumps({"error": f"Overpass API error: {str(e)}"})

        hotels = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            hotels.append({
                "name": tags.get("name", "Unnamed"),
                "type": (
                    tags.get("tourism") or 
                    tags.get("amenity") or 
                    "lodging"
                ),
                "lat": el.get("lat"),
                "lon": el.get("lon")
            })

        return json.dumps({
            "city": city.lower(),
            "radius_km": radius_km,
            "count": len(hotels),
            "hotels": hotels[:20]
        }, indent=2)
