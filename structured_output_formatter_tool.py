import re
import json

# ---- Robust import for AbstractTool ----
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

if AbstractTool is None:
    class AbstractTool:  # fallback
        name: str = ""
        description: str = ""
        def use(self, tool_input: str) -> str:
            raise NotImplementedError


class StructuredOutputFormatterTool(AbstractTool):

    name = "structured_output_formatter"
    description = (
        "Formats an itinerary into structured output. "
        "Default: Markdown table. "
        "If input begins with 'JSON:', returns structured itinerary JSON."
    )

    def _extract_fields(self, line):
        """Extract fields using regex."""
        entry = {
            "day": None,
            "activities": [],
            "restaurant": None,
            "hotel": None,
            "notes": None
        }

        # Day
        if m := re.search(r"Day\s*(\d+)", line, re.I):
            entry["day"] = int(m.group(1))

        # Restaurant
        if m := re.search(
            r"(?:eat at|dinner at|lunch at|breakfast at|snacks at|at)\s+([A-Z][\w’'& .-]+)",
            line,
            re.I
        ):
            entry["restaurant"] = m.group(1).strip()

        # Hotel name
        if m := re.search(r"(?:stay at|hotel:)\s+([A-Z][\w’'& .-]+)", line, re.I):
            entry["hotel"] = m.group(1).strip()

        # Extract activity text (remove day + restaurant + hotel phrases)
        activity = re.sub(r"Day\s*\d+[:\-]?\s*", "", line, flags=re.I)
        activity = re.sub(
            r"(eat at|dinner at|lunch at|breakfast at|snacks at|at)\s+[A-Z][\w’'& .-]+",
            "",
            activity,
            flags=re.I
        )
        activity = re.sub(
            r"(stay at|hotel:)\s+[A-Z][\w’'& .-]+",
            "",
            activity,
            flags=re.I
        )

        activity = activity.strip(" ,.-")
        if activity:
            entry["activities"].append(activity)

        return entry

    def _format_markdown(self, lines):
        rows = []
        for line in lines:
            fields = self._extract_fields(line)
            day = fields["day"] or len(rows) + 1
            activity = ", ".join(fields["activities"]) if fields["activities"] else "—"
            restaurant = fields["restaurant"] or "—"
            rows.append((day, activity, restaurant))

        table = "Day | Activity | Restaurant\n"
        table += "----|----------|-----------\n"
        for d, a, r in rows:
            table += f"{d} | {a} | {r}\n"
        return table

    def _format_json(self, lines):
        itinerary = []
        for line in lines:
            fields = self._extract_fields(line)
            # Assign missing day sequentially
            if fields["day"] is None:
                fields["day"] = len(itinerary) + 1
            itinerary.append(fields)
        return json.dumps({"itinerary": itinerary}, indent=2)

    def use(self, tool_input: str) -> str:
        # JSON mode?
        json_mode = tool_input.strip().lower().startswith("json:")

        if json_mode:
            content = tool_input.split(":", 1)[1].strip()
        else:
            content = tool_input.strip()

        lines = [line for line in content.split("\n") if line.strip()]

        if json_mode:
            return self._format_json(lines)
        return self._format_markdown(lines)
