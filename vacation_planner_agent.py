# vacation_planner_agent.py

# ---- FAIRLIB IMPORTS ----
from fairlib.modules.agent.simple_agent import SimpleAgent
from fairlib import ToolRegistry, ToolExecutor, ReActPlanner, OpenAIAdapter
from fairlib.config import settings

# ---- YOUR TOOL IMPORTS ----
from flight_search_tool import FlightSearchTool
from restaurant_search_tool import RestaurantSearchTool
from activity_search_tool import ActivitySearchTool
from hotel_search_tool import HotelSearchTool
from budget_tool import BudgetTool
from structured_output_formatter_tool import StructuredOutputFormatterTool

# ---- INITIALIZE LLM ----
llm = OpenAIAdapter(api_key=settings.api_keys["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"])

# ---- SIMPLE MEMORY (your FairLib version does NOT include memory module) ----
memory = []      # <<< FIXED

# ---- REGISTER TOOLS ----
tool_registry = ToolRegistry()
tool_registry.register_tool(FlightSearchTool())
tool_registry.register_tool(RestaurantSearchTool())
tool_registry.register_tool(ActivitySearchTool())
tool_registry.register_tool(HotelSearchTool())
tool_registry.register_tool(BudgetTool())
tool_registry.register_tool(StructuredOutputFormatterTool())

# ---- EXECUTOR + PLANNER ----
executor = ToolExecutor(tool_registry)
planner = ReActPlanner(llm, tool_registry)

# ---- CREATE AGENT ----
agent = SimpleAgent(llm, planner, executor, memory)

# ---- DEMO ----
if __name__ == "__main__":
    prompt = """
    Build a 2-day Miami vacation plan for two people.
    Include restaurants, activities, flights from DEN, hotel, and budget.
    Format with structured_output_formatter.
    """

    result = agent.run(prompt)
    print("\n\nFINAL OUTPUT:\n")
    print(result)
