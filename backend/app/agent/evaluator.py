from app.models.schemas import EvaluationResult
from app.agent.loop import AgentLoop
from app.agent.tools.time_tool import GetCurrentTimeTool
from app.agent.tools.calculator import CalculatorTool
from app.agent.tools.web_search import WebSearchTool
from app.agent.tools.fetch_page import FetchPageTool

# Fixed evaluation set
EVALUATION_CASES = [
    {
        "goal": "What is 18% of 450?",
        "expected_keywords": ["81"],
        "notes": "Basic calculator"
    },
    {
        "goal": "What is the capital of Japan?",
        "expected_keywords": ["tokyo"],
        "notes": "Knowledge or search"
    },
    {
        "goal": "What is the current UTC time?",
        "expected_keywords": ["utc", ":"],
        "notes": "Time tool"
    },
    {
        "goal": "Calculate 25% of 800 and tell me the capital of France",
        "expected_keywords": ["200", "paris"],
        "notes": "Mixed tools"
    },
]

def run_evaluation() -> list[EvaluationResult]:
    tools = [
        GetCurrentTimeTool(),
        CalculatorTool(),
        WebSearchTool(),
        FetchPageTool(),
    ]
    agent = AgentLoop(tools=tools)
    results = []

    for case in EVALUATION_CASES:
        from app.models.schemas import AgentRunRequest
        request = AgentRunRequest(goal=case["goal"], max_steps=6)
        response = agent.run(request)

        answer = (response.final_answer or "").lower()
        success = all(kw.lower() in answer for kw in case["expected_keywords"])

        results.append(EvaluationResult(
            goal=case["goal"],
            success=success,
            final_answer=response.final_answer,
            steps_taken=len(response.steps),
            notes=case["notes"]
        ))

    return results