import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.models.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    ApprovalRequest,
    EvaluationResult
)
from app.agent.loop import AgentLoop
from app.agent.tools.time_tool import GetCurrentTimeTool
from app.agent.tools.calculator import CalculatorTool
from app.agent.tools.web_search import WebSearchTool
from app.agent.tools.fetch_page import FetchPageTool
from app.agent.evaluator import run_evaluation
from app.core.database import engine, Base, get_db
from app.models.db_models import AgentRun

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Agent Harness",
    description="Week 3 - Reliability + Human-in-the-loop + Evaluation",
    version="0.3.0"
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register tools
tools = [
    GetCurrentTimeTool(),
    CalculatorTool(),
    WebSearchTool(),
    FetchPageTool(),
]

agent = AgentLoop(tools=tools)

@app.get("/")
def health():
    return {
        "status": "ok",
        "version": "week-3",
        "message": "AI Agent Harness is running"
    }

@app.post("/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest):
    """
    Run the agent.
    Set require_approval=true if you want human approval before finalizing.
    """
    return agent.run(request)

@app.post("/agent/approve")
def approve_run(payload: ApprovalRequest, db: Session = Depends(get_db)):
    """
    Approve or reject a run that is in 'waiting_approval' status.
    """
    run = db.query(AgentRun).filter(AgentRun.id == payload.run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.status != "waiting_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Run is in '{run.status}' status. Only 'waiting_approval' runs can be approved."
        )

    if payload.approved:
        run.status = "completed"
    else:
        run.status = "rejected"
        if payload.feedback:
            run.final_answer = f"[Rejected] Feedback: {payload.feedback}"

    db.commit()
    db.refresh(run)

    return {
        "message": "Run updated successfully",
        "run_id": run.id,
        "status": run.status,
        "final_answer": run.final_answer
    }

@app.get("/agent/runs")
def list_runs(limit: int = 20, db: Session = Depends(get_db)):
    """
    Get the latest agent runs.
    """
    runs = (
        db.query(AgentRun)
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
        .all()
    )

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

@app.get("/agent/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)):
    """
    Get a specific run with all its steps.
    """
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "id": run.id,
        "goal": run.goal,
        "status": run.status,
        "final_answer": run.final_answer,
        "created_at": run.created_at,
        "steps": [
            {
                "step_number": s.step_number,
                "thought": s.thought,
                "action_tool": s.action_tool,
                "action_args": s.action_args,
                "observation": s.observation,
                "is_final": s.is_final
            }
            for s in sorted(run.steps, key=lambda x: x.step_number)
        ]
    }

@app.get("/agent/evaluate", response_model=list[EvaluationResult])
def evaluate_agent():
    """
    Run a fixed set of evaluation cases and return the results.
    """
    return run_evaluation()