import json
from openai import OpenAI
from app.core.config import settings
from app.agent.tools.base import BaseTool

client = OpenAI(api_key=settings.openai_api_key)

def call_llm(messages: list[dict], tools: list[BaseTool]) -> dict:
    """
    Calls the LLM and forces a structured JSON response.
    Returns a dict with: thought, action, is_final, final_answer
    """

    tool_descriptions = "\n".join(
        [f"- {t.name}: {t.description}" for t in tools]
    )

    # We inject available tools into the system message for Week 1 simplicity
    if messages and messages[0]["role"] == "system":
        messages[0]["content"] += f"\n\nAvailable tools:\n{tool_descriptions}"

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback if the model returns invalid JSON
        return {
            "thought": "Failed to parse model response",
            "action": None,
            "is_final": True,
            "final_answer": content
        }

    # Normalize the response
    return {
        "thought": data.get("thought", ""),
        "action": data.get("action"),
        "is_final": bool(data.get("is_final", False)),
        "final_answer": data.get("final_answer")
    }