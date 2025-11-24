from openai import OpenAI
from fairlib.core.message import Message  # IMPORTANT

class OpenAILLM:
    """
    FAIR-LLM compatible wrapper around OpenAI Chat Completions API.
    The ReActPlanner will call .ainvoke(messages) with a list of Message objects.
    """

    def __init__(self, model="gpt-4o-mini", api_key=None):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    async def ainvoke(self, messages):
        """
        FAIR-LLM passes a list of Message(role, content).
        Convert them to OpenAI format and return the assistant reply string.
        """

        # Convert FAIR-LLM Message objects → OpenAI dictionaries
        openai_msgs = []
        for m in messages:
            openai_msgs.append({
                "role": m.role,
                "content": m.content
            })

        # Call OpenAI API (sync in async wrapper — acceptable for class project)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=openai_msgs,
            temperature=0.4,
            max_tokens=400
        )

        return resp.choices[0].message["content"]
