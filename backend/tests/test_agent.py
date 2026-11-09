import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

def run_test(goal: str, max_steps: int = 8) -> dict:
    payload = {
        "goal": goal,
        "max_steps": max_steps
    }
    response = requests.post(f"{BASE_URL}/agent/run", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def print_result(test_name: str, data: dict, expected_keywords: Optional[list] = None):
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)
    print(f"Goal           : {data['goal']}")
    print(f"Status         : {data['status']}")
    print(f"Final Answer   : {data.get('final_answer')}")
    print(f"Total Steps    : {len(data['steps'])}")
    print("-" * 70)

    for step in data["steps"]:
        print(f"\nStep {step['step_number']}:")
        print(f"  Thought     : {step['thought'][:200]}{'...' if len(step['thought']) > 200 else ''}")
        if step.get("action"):
            print(f"  Action      : {step['action']['tool']} | {step['action']['args']}")
        if step.get("observation"):
            obs = step["observation"]
            print(f"  Observation : {obs[:250]}{'...' if len(obs) > 250 else ''}")
        print(f"  Is Final    : {step['is_final']}")

    if expected_keywords and data.get("final_answer"):
        answer = data["final_answer"].lower()
        missing = [kw for kw in expected_keywords if kw.lower() not in answer]
        if missing:
            print(f"\n⚠️  Warning: Expected keywords missing → {missing}")
        else:
            print("\n✅ Keywords found in final answer")

def main():
    print("\n🚀 Starting Week 2 Agent Tests...\n")

    # --------------------------------------------------
    # Week 1 Regression Tests
    # --------------------------------------------------
    data = run_test("What is 18% of 450?")
    print_result("Calculator - 18% of 450", data, expected_keywords=["81"])

    data = run_test("What is the current UTC time?")
    print_result("Current Time", data)

    data = run_test("What is the capital of France?")
    print_result("No tool needed", data, expected_keywords=["paris"])

    # --------------------------------------------------
    # Week 2 - Web Search
    # --------------------------------------------------
    data = run_test("What are the key new features in NestJS 11?")
    print_result("Web Search - NestJS 11", data)

    data = run_test("Who won the last ICC Cricket World Cup?")
    print_result("Web Search - Cricket World Cup", data)

    # --------------------------------------------------
    # Week 2 - Fetch Page
    # --------------------------------------------------
    data = run_test("Summarize the main content of https://fastapi.tiangolo.com")
    print_result("Fetch Page - FastAPI homepage", data)

    # --------------------------------------------------
    # Week 2 - Mixed tools
    # --------------------------------------------------
    data = run_test("What is 15% of 340? Also search for the capital of Japan.")
    print_result("Mixed tools (Calculator + Search)", data, expected_keywords=["51"])

    # --------------------------------------------------
    # Max steps protection
    # --------------------------------------------------
    data = run_test("Keep searching for random topics forever", max_steps=3)
    print_result("Max steps protection", data)
    if data["status"] == "max_steps_reached":
        print("✅ Correctly stopped at max steps")
    else:
        print("❌ Did not respect max_steps")

    # --------------------------------------------------
    # Check that runs are being saved
    # --------------------------------------------------
    print("\n" + "=" * 70)
    print("Checking saved runs in database...")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/agent/runs")
        response.raise_for_status()
        runs = response.json()
        print(f"✅ Found {len(runs)} saved runs in the database")
        if runs:
            print(f"Latest run goal: {runs[0]['goal']}")
    except Exception as e:
        print(f"❌ Failed to fetch runs: {e}")

    print("\n" + "=" * 70)
    print("✅ All Week 2 tests finished")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()