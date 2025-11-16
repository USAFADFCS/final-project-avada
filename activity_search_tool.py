import json
import requests
from fairlib.core.interfaces.tools import AbstractTool

CITY_COORDS = {
    "miami": (25.7617, -80.1918),
    "denver": (39.7392, -104.9903),
    "orlando": (28.5383, -81.3792),
    "los angeles": (34.0522, -118.2437),
    "new york": (40.7128, -74.0060),
    "chicago": (41.8781, -87.6298),
    "dallas": (32.7767, -96.7970),
}

class ActivitySearchTool(AbstractTool):

    name = "activity_search"
    description = (
        "Finds attractions, museums, parks, beaches, and activities near a city "
        "using the OpenStreetMap Overpass API. Requires 'city'; optional 'radius_km'."
    )

    def _get_coords(self, city: str):
        city = city.lower()
        return CITY_COORDS.get(city)

    def _query_overpass(self, lat, lon, radius_km):
        radius_m = radius_km * 1000

        query = f"""
        [out:json];
        (
          node["tourism"="attraction"](around:{radius_m},{lat},{lon});
          node["tourism"="museum"](around:{radius_m},{lat},{lon});
          node["tourism"="gallery"](around:{radius_m},{lat},{lon});
          node["tourism"="zoo"](around:{radius_m},{lat},{lon});
          node["tourism"="aquarium"](around:{radius_m},{lat},{lon});
          node["tourism"="theme_park"](around:{radius_m},{lat},{lon});
          node["leisure"="park"](around:{radius_m},{lat},{lon});
          node["leisure"="beach_resort"](around:{radius_m},{lat},{lon});
          node["natural"="beach"](around:{radius_m},{lat},{lon});
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
        radius_km = payload.get("radius_km", 5)

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

        activities = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            activities.append({
                "name": tags.get("name", "Unnamed"),
                "type": tags.get("tourism") or tags.get("leisure") or tags.get("natural"),
                "lat": el.get("lat"),
                "lon": el.get("lon")
            })

        return json.dumps({
            "city": city.lower(),
            "radius_km": radius_km,
            "count": len(activities),
            "activities": activities[:20]  # Limit output
        }, indent=2)
