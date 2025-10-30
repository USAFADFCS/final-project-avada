# structured_output_formatter_tool.py
import re

# ---- Robust import for AbstractTool (works even if paths differ) ----
AbstractTool = None
for path in (
    "fairlib.core.interfaces.tools",
    "core.interfaces.tools",
    "fairlib.interfaces.tools",
):
    try:
        mod = __import__(path, fromlist=["AbstractTool"])
        AbstractTool = getattr(mod, "AbstractTool")
        break
    except Exception:
        pass

# Minimal fallback so the tool still works without the framework import
if AbstractTool is None:
    class AbstractTool:  # type: ignore
        name: str = ""
        description: str = ""
        def use(self, tool_input: str) -> str:  # pragma: no cover
            raise NotImplementedError

# ---- Your tool implementation ----
class StructuredOutputFormatterTool(AbstractTool):
    """
    Formats itinerary text into a Markdown table:
    Day | Activity | Restaurant
    """
    name = "structured_output_formatter"
    description = (
        "Formats an unstructured itinerary into a clean Markdown table. "
        "Input should contain day-by-day text describing activities and restaurants. "
        "Example: 'Day 1: Fly to Miami, dinner at Joe’s Stone Crab.'"
    )

    def use(self, tool_input: str) -> str:
        lines = [line.strip() for line in tool_input.split("\n") if line.strip()]

        rows = []
        for line in lines:
            # Day number (defaults to sequential if missing)
            m_day = re.search(r"Day\s*(\d+)", line, re.IGNORECASE)
            day = m_day.group(1) if m_day else str(len(rows) + 1)

            # Restaurant (optional)
            restaurant = None
            m_rest = re.search(r"(?:eat at|dinner at|lunch at|at)\s+([A-Z][\w’'& .-]+)", line, re.IGNORECASE)
            if m_rest:
                restaurant = m_rest.group(1).strip()

            # Clean activity text
            activity = re.sub(r"Day\s*\d+[:\-]?\s*", "", line, flags=re.IGNORECASE)
            if restaurant:
                activity = re.sub(r"(?:eat at|dinner at|lunch at|at)\s+[A-Z][\w’'& .-]+", "", activity, flags=re.IGNORECASE)
            activity = activity.strip(",. ").strip()

            rows.append((day, activity, restaurant or "—"))

        table = "Day | Activity | Restaurant\n"
        table += "----|-----------|-----------\n"
        for d, a, r in rows:
            table += f"{d} | {a} | {r}\n"
        return table
