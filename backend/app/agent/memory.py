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
        return """You are a careful ReAct-style agent.

You must respond in valid JSON only with these fields:
{
  "thought": "your reasoning",
  "action": {"tool": "tool_name", "args": {...}} or null,
  "is_final": true/false,
  "final_answer": "the final answer if is_final is true, otherwise null"
}

Rules:
- Think step by step in the "thought" field.
- Use a tool when you need information or calculation.
- "args" must always be a JSON object whose keys are the tool's input parameter names; never provide a bare string or other value.
- For example, call the calculator with "args": {"expression": "0.15 * 340"}.
- When you have enough information, set is_final=true and give the final_answer.
- Never invent tool results. Only use the Observation you receive.
"""