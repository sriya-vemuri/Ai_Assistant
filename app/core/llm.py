import os
from ollama import Client, Options

# Initialize Ollama client with configurable host
ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
ollama = Client(host=ollama_host)
MODEL = "mistral"  # Ollama’s default 7B model

async def generate_response(prompt: str, max_tokens: int = 256) -> str:
    opts = Options(max_tokens=max_tokens)
    resp = ollama.generate(
        model=MODEL,
        prompt=prompt,
        options=opts
    )
    try:
        return resp.response.strip()
    except AttributeError:
        if hasattr(resp, "choices"):
            return resp.choices[0].text.strip()
        return str(resp).strip()

# Smoke-test when run directly
if __name__ == "__main__":
    import asyncio
    print("Make sure you have run: ollama run mistral in another terminal (or it’s running in the container)")
    reply = asyncio.run(generate_response("Say hello in one sentence."))
    print("SMOKE TEST:", reply)