from fairlib import SimpleAgent, ReActPlanner, ToolExecutor, ToolRegistry, HuggingFaceAdapter
from destination_matcher_tool import DestinationMatcherTool
from structured_output_formatter_tool import StructuredOutputFormatterTool

# 1. Load the small model (TinyLlama)
llm = HuggingFaceAdapter(model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# 2. Register tools
tool_registry = ToolRegistry()
tool_registry.register_tool(DestinationMatcherTool())
tool_registry.register_tool(StructuredOutputFormatterTool())

# 3. Create executor + planner + agent
executor = ToolExecutor(tool_registry)
planner = ReActPlanner(llm, tool_registry)
agent = SimpleAgent(llm=llm, planner=planner, tool_executor=executor)
