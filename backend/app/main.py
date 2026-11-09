from fastapi import FastAPI
from app.models.schemas import AgentRunRequest, AgentRunResponse
from app.agent.loop import AgentLoop
from app.agent.tools.time_tool import GetCurrentTimeTool
from app.agent.tools.calculator import CalculatorTool

app = FastAPI(title="AI Agent Harness - Week 1")

tools = [
    GetCurrentTimeTool(),
    CalculatorTool()
]

agent = AgentLoop(tools=tools)

@app.get("/")
def health():
    return {"status": "ok", "message": "AI Agent Harness is running"}

@app.post("/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest):
    return agent.run(request)