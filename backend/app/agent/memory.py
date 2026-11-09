from typing import List
from app.models.schemas import AgentStep

class AgentMemory:
    def __init__(self, goal: str):
        self.goal = goal
        self.steps: List[AgentStep] = []

    def add_step(self, step: AgentStep) -> None:
        self.steps.append(step)

    def get_messages_for_llm(self) -> list[dict]:
        messages = [
            {
                "role": "system",
                "content": self._system_prompt()
            },
            {
                "role": "user",
                "content": f"Goal: {self.goal}"
            }
        ]

        for step in self.steps:
            # Assistant thought
            messages.append({
                "role": "assistant",
                "content": f"Thought: {step.thought}"
            })

            if step.action:
                messages.append({
                    "role": "assistant",
                    "content": f"Action: {step.action.tool} | Args: {step.action.args}"
                })

            if step.observation is not None:
                messages.append({
                    "role": "user",
                    "content": f"Observation: {step.observation}"
                })

        return messages

    def _system_prompt(self) -> str:
        return """You are a careful and reliable ReAct-style AI agent.

You must respond in valid JSON only using this exact schema:
{
  "thought": "your step-by-step reasoning",
  "action": {"tool": "tool_name", "args": {...}} or null,
  "is_final": true or false,
  "final_answer": "the final answer only when is_final is true, otherwise null"
}

Rules:
1. Always think before acting.
2. Use tools when you need external information or calculation.
3. Never invent tool results — only use the Observation you receive.
4. If a tool fails, try a different approach or different query.
5. When you have enough information, set is_final = true and give a clear final_answer.
6. Keep final_answer concise and direct.
7. Prefer using tools over guessing when the information can change.
"""