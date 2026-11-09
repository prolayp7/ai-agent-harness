'''
These are the contracts of your harness.
AgentStep → one iteration of the loop
AgentRunResponse → the full result you will return from the API

'''

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any
from datetime import datetime

class ToolCall(BaseModel):
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)

class AgentStep(BaseModel):
    step_number: int
    thought: str
    action: Optional[ToolCall] = None
    observation: Optional[str] = None
    is_final: bool = False

class AgentRunRequest(BaseModel):
    goal: str
    max_steps: int = 8
    require_approval: bool = False

class AgentRunResponse(BaseModel):
    run_id: str
    goal: str
    steps: List[AgentStep]
    final_answer: Optional[str] = None
    status: Literal["completed", "max_steps_reached", "waiting_approval", "error"]
    created_at: datetime