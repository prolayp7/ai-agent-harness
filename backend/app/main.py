from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import (
    AgentRunRequest, AgentRunResponse, ApprovalRequest, EvaluationResult
)
from app.agent.loop import AgentLoop
from app.agent.tools.time_tool import GetCurrentTimeTool
from app.agent.tools.calculator import CalculatorTool
from app.agent.tools.web_search import WebSearchTool
from app.agent.tools.fetch_page import FetchPageTool
from app.agent.evaluator import run_evaluation
from app.core.database import engine, Base, get_db
from app.models.db_models import AgentRun

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Agent Harness - Week 3")

tools = [
    GetCurrentTimeTool(),
    CalculatorTool(),
    WebSearchTool(),
    FetchPageTool(),
]
agent = AgentLoop(tools=tools)

@app.get("/")
def health():
    return {"status": "ok", "version": "week-3"}

@app.post("/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest):
    return agent.run(request)

@app.post("/agent/approve")
def approve_run(payload: ApprovalRequest, db: Session = Depends(get_db)):
    run = db.query(AgentRun).filter(AgentRun.id == payload.run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if payload.approved:
        run.status = "completed"
    else:
        run.status = "rejected"
        if payload.feedback:
            run.final_answer = f"Rejected. Feedback: {payload.feedback}"

    db.commit()
    return {"message": "Updated", "status": run.status}

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

@app.get("/agent/evaluate", response_model=list[EvaluationResult])
def evaluate_agent():
    """Run a fixed set of evaluation cases"""
    return run_evaluation()