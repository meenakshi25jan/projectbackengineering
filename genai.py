import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_analyze(role: str, context: str) -> str:
    """Quick deep analysis of project context."""
    messages = [
        {"role": "system", "content": f"You are an expert {role} and reverse-engineer."},
        {"role": "user", "content": f"Analyze this project:\n\n{context}"}
    ]
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

def generate_markdown_doc(context: str, prompt: str, system: str = None) -> str:
    """Generate structured markdown documentation with OpenAI."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": f"{prompt}\n\nContext:\n{context}"})

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
