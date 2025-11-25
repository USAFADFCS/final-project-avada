from groq import Groq

class TinyLlamaLLM:
    """
    LLM wrapper that uses Groq’s API instead of HuggingFace.
    This completely avoids all HF model downloads.
    """

    def __init__(self, model_name="llama3-8b-8192"):
        self.client = Groq(api_key="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")
        self.model_name = model_name

    async def ainvoke(self, messages):
        return self.invoke(messages)

    def invoke(self, messages):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message["content"]

    async def achat(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.invoke(messages)
