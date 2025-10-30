# vacation_planner.py — tool-only demo for midpoint
from structured_output_formatter_tool import StructuredOutputFormatterTool

itinerary = """
Day 1: Fly to Miami, check in to hotel, dinner at Joe’s Stone Crab.
Day 2: Go surfing and eat at Havana 1957.
Day 3: Visit Biscayne Park, lunch at Yardbird.
"""

tool = StructuredOutputFormatterTool()
print(tool.use(itinerary))
