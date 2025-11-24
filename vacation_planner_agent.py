# vacation_planner_agent.py

import asyncio

# =========================
#   FAIRLIB IMPORTS
# =========================

# Local LLaMA-style model included in YOUR version of fairlib
from fairlib.modules.llm.llama_llm import LlamaLLM

from fairlib.modules.planning.react_planner import ReActPlanner
from fairlib.modules.agent.simple_agent import SimpleAgent
from fairlib.modules.action.tools.registry import ToolRegistry

# =========================
#   YOUR TOOL IMPORTS
# =========================

from flight_search_tool import FlightSearchTool
from restaurant_search_tool import RestaurantSearchTool
from activity_search_tool import ActivitySearchTool
from hotel_search_tool import HotelSearchTool
from budget_tool import BudgetTool
from structured_output_formatter_tool import StructuredOutputFormatterTool


# =========================
#   SIMPLE MEMORY
# =========================

class SimpleMemory:
    """
    Minimal memory class compatible with SimpleAgent.
    Stores Message objects from fairlib.core.message.
    """

    def __init__(self):
        self._history = []

    def add_message(self, msg):
        self._history.append(msg)

    def get_history(self):
        return list(self._history)

    def clear(self):
        self._history.clear()


# =========================
#   SIMPLE TOOL EXECUTOR
# =========================

class SimpleToolExecutor:
    """
    Looks up tools in ToolRegistry and calls their .use() method.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_name: str, tool_input: str) -> str:
        tool = self.registry.get_tool(tool_name)
        if tool is None:
            return f"Error: Tool '{tool_name}' not found."

        try:
            return tool.use(tool_input)
        except Exception as e:
            return f"Error running tool '{tool_name}': {e}"


# =========================
#   BUILD VACATION AGENT
# =========================

def build_vacation_agent() -> SimpleAgent:

    # 1. Load LLaMA LLM (NO API KEY needed)
    llm = LlamaLLM()

    # 2. Register tools
    registry = ToolRegistry()
    registry.register_tool(FlightSearchTool())
    registry.register_tool(RestaurantSearchTool())
    registry.register_tool(ActivitySearchTool())
    registry.register_tool(HotelSearchTool())
    registry.register_tool(BudgetTool())
    registry.register_tool(StructuredOutputFormatterTool())

    # 3. Create planner
    planner = ReActPlanner(llm, registry)

    # 4. Create executor + memory
    executor = SimpleToolExecutor(registry)
    memory = SimpleMemory()

    # 5. Build the SimpleAgent
    agent = SimpleAgent(
        llm=llm,
        planner=planner,
        tool_executor=executor,
        memory=memory,
        max_steps=6,      # number of ReAct steps
        stateless=False,  # keep memory between steps
    )

    return agent


# =========================
#   ONE-SHOT REQUEST
# =========================

async def run_single():
    agent = build_vacation_agent()

    query = (
        "Plan a 4-day Miami vacation for two college students. "
        "We are flying from DEN. Budget is $1600 total. "
        "We like beaches, nightlife, cheap food, and fun activities. "
        "Give me the final answer as a markdown itinerary table."
    )

    result = await agent.arun(query)
    print("\n\n===== VACATION PLAN =====\n")
    print(result)


# =========================
#   INTERACTIVE CHAT
# =========================

async def chat():
    agent = build_vacation_agent()
    print("✨ Vacation Planner Ready! Type your request or 'quit'.")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in {"quit", "exit"}:
            break

        print("\nAgent:\n")
        answer = await agent.arun(user_input)
        print(answer)


# =========================
#   MAIN ENTRY
# =========================

if __name__ == "__main__":
    # Option 1: run one predefined vacation plan
    # asyncio.run(run_single())

    # Option 2: interactive mode
    asyncio.run(chat())
