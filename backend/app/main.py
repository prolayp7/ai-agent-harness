from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.models.schemas import AgentRunRequest, AgentRunResponse
from app.agent.loop import AgentLoop
from app.agent.tools.time_tool import GetCurrentTimeTool
from app.agent.tools.calculator import CalculatorTool
from app.agent.tools.web_search import WebSearchTool
from app.agent.tools.fetch_page import FetchPageTool
from app.core.database import engine, Base, get_db
from app.models.db_models import AgentRun

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Agent Harness - Week 2")

tools = [
    GetCurrentTimeTool(),
    CalculatorTool(),
    WebSearchTool(),
    FetchPageTool(),
]

agent = AgentLoop(tools=tools)

@app.get("/")
def health():
    return {"status": "ok", "message": "AI Agent Harness Week 2 is running"}

@app.post("/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest):
    return agent.run(request)

@app.get("/agent/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "goal": r.goal,
            "status": r.status,
            "final_answer": r.final_answer,
            "created_at": r.created_at
        }
        for r in runs
    ]