import json
from fairlib.core.interfaces.tools import AbstractTool

class BudgetTool(AbstractTool):

    name = "trip_budget"
    description = (
        "Calculates trip cost. Inputs: travelers, days, flight_cost, hotel_per_night, "
        "food_per_day, activities_total, misc, tax_multiplier. Returns detailed breakdown."
    )

    def use(self, tool_input: str) -> str:
        try:
            data = json.loads(tool_input)
        except:
            return json.dumps({"error": "Invalid JSON input."})

        # Extract fields with defaults
        travelers = data.get("travelers", 1)
        days = data.get("days", 1)
        flight_cost = data.get("flight_cost", 0)
        hotel_per_night = data.get("hotel_per_night", 0)
        food_per_day = data.get("food_per_day", 0)
        activities_total = data.get("activities_total", 0)
        misc = data.get("misc", 0)
        tax_multiplier = data.get("tax_multiplier", 1.0)

        # Compute categories
        hotel_total = hotel_per_night * days
        food_total = food_per_day * days * travelers
        subtotal = (
            flight_cost * travelers +
            hotel_total +
            food_total +
            activities_total +
            misc
        )
        total_cost = subtotal * tax_multiplier
        per_person = total_cost / travelers if travelers > 0 else total_cost

        result = {
            "inputs": data,
            "breakdown": {
                "flight_total": flight_cost * travelers,
                "hotel_total": hotel_total,
                "food_total": food_total,
                "activities_total": activities_total,
                "misc_total": misc,
                "subtotal": subtotal,
                "tax_multiplier": tax_multiplier,
                "total_after_tax": total_cost
            },
            "per_person_cost": per_person,
            "total_group_cost": total_cost
        }

        return json.dumps(result, indent=2)
