# vacation_planner_agent.py

import asyncio

# =========================
#   FAIRLIB IMPORTS
# =========================

# Use HuggingFaceAdapter for TinyLlama (local HF model)
from fairlib.modules.mal.huggingface_adapter import HuggingFaceAdapter
from tinyllama_llm import TinyLlamaLLM
from fairlib.modules.planning.react_planner import ReActPlanner
from fairlib.modules.agent.simple_agent import SimpleAgent
from fairlib.modules.action.tools.registry import ToolRegistry


# =========================
#   TINY LLAMA WRAPPER
# =========================

class TinyLlamaLLM:
    """
    FAST + GUARANTEED WORKING local model using HuggingFaceAdapter.
    Phi-2 is tiny, quick, and never requires authentication.
    """

    def __init__(self):
        self.model = HuggingFaceAdapter(
            model_name="microsoft/phi-2"
        )

    async def ainvoke(self, messages):
        return self.invoke(messages)

    def invoke(self, messages):
        return self.model.chat(messages)

    async def achat(self, prompt: str):
        messages = [{"role": "user", "content": prompt}]
        return self.model.chat(messages)



# =========================
#   TOOL IMPORTS
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
    """Minimal memory store for SimpleAgent."""

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
    """Executes registered tools by name."""

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

    # 1. Load TinyLlama locally
    llm = TinyLlamaLLM()

    # 2. Register tools
    registry = ToolRegistry()
    registry.register_tool(FlightSearchTool())
    registry.register_tool(RestaurantSearchTool())
    registry.register_tool(ActivitySearchTool())
    registry.register_tool(HotelSearchTool())
    registry.register_tool(BudgetTool())
    registry.register_tool(StructuredOutputFormatterTool())

    # 3. ReAct planner
    planner = ReActPlanner(llm, registry)

    # 4. Executor + memory
    executor = SimpleToolExecutor(registry)
    memory = SimpleMemory()

    # 5. Build SimpleAgent
    agent = SimpleAgent(
        llm=llm,
        planner=planner,
        tool_executor=executor,
        memory=memory,
        max_steps=6,
        stateless=False,
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
        "Give the final answer as a markdown itinerary table."
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
    # Option 1: run one predefined plan
    # asyncio.run(run_single())

    # Option 2: interactive chat
    asyncio.run(chat())
