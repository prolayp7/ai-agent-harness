import uuid
from datetime import datetime, timezone
from inspect import Parameter, signature
from typing import Any
from sqlalchemy.orm import Session

from app.models.schemas import AgentRunRequest, AgentRunResponse, AgentStep, ToolCall
from app.models.db_models import AgentRun, AgentStepDB
from app.agent.memory import AgentMemory
from app.agent.tools.base import BaseTool
from app.agent.llm import call_llm
from app.core.database import SessionLocal

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

            if action_data and not is_final:
                tool_name = action_data.get("tool")
                tool_args = action_data.get("args", {})

                if not isinstance(tool_name, str) or not tool_name:
                    observation = "Error: tool name must be a non-empty string"
                elif tool_name in self.tools:
                    try:
                        tool_args = self._normalize_tool_args(
                            self.tools[tool_name], tool_args
                        )
                    except ValueError as e:
                        step.action = ToolCall(tool=tool_name, args={})
                        observation = f"Tool error: {e}"
                    else:
                        step.action = ToolCall(tool=tool_name, args=tool_args)
                        try:
                            observation = self.tools[tool_name].run(**tool_args)
                        except Exception as e:
                            observation = f"Tool error: {str(e)}"
                else:
                    step.action = ToolCall(
                        tool=tool_name,
                        args=tool_args if isinstance(tool_args, dict) else {},
                    )
                    observation = f"Error: Unknown tool '{tool_name}'"

                step.observation = observation

            memory.add_step(step)

            if is_final:
                break
        else:
            status = "max_steps_reached"

        # ----- Save to database -----
        self._save_run(run_id, request.goal, status, final_answer, memory.steps)

        return AgentRunResponse(
            run_id=run_id,
            goal=request.goal,
            steps=memory.steps,
            final_answer=final_answer,
            status=status,
            created_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def _normalize_tool_args(tool: BaseTool, args: object) -> dict[str, Any]:
        if isinstance(args, dict):
            return args

        parameters = [
            parameter
            for parameter in signature(tool.run).parameters.values()
            if parameter.kind
            in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
        ]
        if len(parameters) == 1:
            return {parameters[0].name: args}

        raise ValueError("tool arguments must be a JSON object")

    def _save_run(self, run_id: str, goal: str, status: str, final_answer: str | None, steps: list[AgentStep]):
        db: Session = SessionLocal()
        try:
            db_run = AgentRun(
                id=run_id,
                goal=goal,
                status=status,
                final_answer=final_answer,
                created_at=datetime.now(timezone.utc)
            )
            db.add(db_run)

            for step in steps:
                db_step = AgentStepDB(
                    run_id=run_id,
                    step_number=step.step_number,
                    thought=step.thought,
                    action_tool=step.action.tool if step.action else None,
                    action_args=step.action.args if step.action else None,
                    observation=step.observation,
                    is_final=step.is_final
                )
                db.add(db_step)

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Failed to save run: {e}")
        finally:
            db.close()