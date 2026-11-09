# app/agent/loop.py

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    AgentStep,
    ToolCall
)
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

            thought = llm_output.get("thought", "")
            action_data = llm_output.get("action")
            is_final = bool(llm_output.get("is_final", False))
            final_answer = llm_output.get("final_answer")

            step = AgentStep(
                step_number=step_num,
                thought=thought,
                is_final=is_final
            )

            # Execute tool if the agent requested one
            if action_data and not is_final:
                tool_name = action_data.get("tool")
                tool_args = action_data.get("args", {}) or {}

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

            # ---------- Human-in-the-loop ----------
            if is_final:
                if request.require_approval:
                    status = "waiting_approval"
                    self._save_run(
                        run_id=run_id,
                        goal=request.goal,
                        status=status,
                        final_answer=final_answer,
                        steps=memory.steps
                    )
                    return AgentRunResponse(
                        run_id=run_id,
                        goal=request.goal,
                        steps=memory.steps,
                        final_answer=final_answer,
                        status=status,
                        created_at=datetime.now(timezone.utc)
                    )
                else:
                    break

        else:
            # Loop finished without is_final=True
            status = "max_steps_reached"

        # Normal completion path
        self._save_run(
            run_id=run_id,
            goal=request.goal,
            status=status,
            final_answer=final_answer,
            steps=memory.steps
        )

        return AgentRunResponse(
            run_id=run_id,
            goal=request.goal,
            steps=memory.steps,
            final_answer=final_answer,
            status=status,
            created_at=datetime.now(timezone.utc)
        )

    def _save_run(
        self,
        run_id: str,
        goal: str,
        status: str,
        final_answer: str | None,
        steps: list[AgentStep]
    ) -> None:
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
            print(f"[Error] Failed to save run {run_id}: {e}")
        finally:
            db.close()