import json
from fairlib.core.interfaces.tools import AbstractTool


class DestinationMatcherTool(AbstractTool):

    name = "destination_matcher"
    description = (
        "Given a list of preferred activities and a starting state, "
        "this tool picks 3 beach destinations that match the user's preferences. "
        "Input must be a JSON string with 'activities' and 'starting_state'."
    )

    def use(self, tool_input: str) -> str:
        try:
            data = json.loads(tool_input)
            activities = data.get("activities", [])
            starting_state = data.get("starting_state", "")

            # fake simple logic — perfect for an MVP
            beaches = [
                {"destination": "Miami, Florida", "match": 0.92},
                {"destination": "San Diego, California", "match": 0.87},
                {"destination": "Myrtle Beach, South Carolina", "match": 0.81},
            ]

            return json.dumps({
                "recommended_destinations": beaches,
                "starting_state": starting_state,
                "activities_considered": activities
            })

        except Exception as e:
            return f"Error in DestinationMatcherTool: {str(e)}"
