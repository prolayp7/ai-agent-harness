import uuid
from datetime import datetime, timezone
from app.models.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    AgentStep,
    ToolCall
)
from app.agent.memory import AgentMemory
from app.agent.tools.base import BaseTool
from app.agent.llm import call_llm

class AgentLoop:
    def __init__(self, tools: list[BaseTool]):
        self.tools = {tool.name: tool for tool in tools}

    def run(self, request: AgentRunRequest) -> AgentRunResponse:
        run_id = str(uuid.uuid4())
        memory = AgentMemory(goal=request.goal)
        final_answer = None
        status = "completed"

        for step_num in range(1, request.max_steps + 1):
            messages = memory.get_messages_for_llm()
            llm_output = call_llm(messages, tools=list(self.tools.values()))

            thought = llm_output["thought"]
            action_data = llm_output.get("action")
            is_final = llm_output["is_final"]
            final_answer = llm_output.get("final_answer")

            step = AgentStep(
                step_number=step_num,
                thought=thought,
                is_final=is_final
            )

            # If the agent wants to use a tool
            if action_data and not is_final:
                tool_name = action_data.get("tool")
                tool_args = action_data.get("args", {})

                step.action = ToolCall(tool=tool_name, args=tool_args)

                if tool_name in self.tools:
                    try:
                        observation = self.tools[tool_name].run(**tool_args)
                    except Exception as e:
                        observation = f"Tool error: {str(e)}"
                else:
                    observation = f"Error: Unknown tool '{tool_name}'"

                step.observation = observation

            memory.add_step(step)

            if is_final:
                break
        else:
            status = "max_steps_reached"

        return AgentRunResponse(
            run_id=run_id,
            goal=request.goal,
            steps=memory.steps,
            final_answer=final_answer,
            status=status,
            created_at=datetime.now(timezone.utc)
        )