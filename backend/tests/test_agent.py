import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

def run_test(goal: str, max_steps: int = 8, expected_status: str = "completed") -> dict:
    payload = {
        "goal": goal,
        "max_steps": max_steps
    }

    response = requests.post(f"{BASE_URL}/agent/run", json=payload)
    response.raise_for_status()
    data = response.json()
    return data

def print_result(test_name: str, data: dict, expected_keywords: Optional[list] = None):
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)
    print(f"Goal           : {data['goal']}")
    print(f"Status         : {data['status']}")
    print(f"Final Answer   : {data.get('final_answer')}")
    print(f"Total Steps    : {len(data['steps'])}")
    print("-"*70)

    for step in data["steps"]:
        print(f"\nStep {step['step_number']}:")
        print(f"  Thought     : {step['thought']}")
        if step.get("action"):
            print(f"  Action      : {step['action']['tool']} | {step['action']['args']}")
        if step.get("observation"):
            print(f"  Observation : {step['observation']}")
        print(f"  Is Final    : {step['is_final']}")

    if expected_keywords and data.get("final_answer"):
        answer = data["final_answer"].lower()
        missing = [kw for kw in expected_keywords if kw.lower() not in answer]
        if missing:
            print(f"\n⚠️  Warning: Expected keywords missing → {missing}")
        else:
            print("\n✅ Keywords found in final answer")

def main():
    print("\n🚀 Starting Week 1 Agent Tests...\n")

    # Test 1
    data = run_test("What is 18% of 450?")
    print_result("Calculator - 18% of 450", data, expected_keywords=["81"])

    # Test 2
    data = run_test("What is the current UTC time?")
    print_result("Current Time", data)

    # Test 3
    data = run_test("What is 15% of 340? Then tell me the current UTC time.")
    print_result("Two-step reasoning", data, expected_keywords=["51"])

    # Test 4
    data = run_test("What is the capital of France?")
    print_result("No tool needed", data, expected_keywords=["paris"])

    # Test 5 - Max steps
    data = run_test("Keep calculating random percentages forever", max_steps=3)
    print_result("Max steps protection", data)
    if data["status"] == "max_steps_reached":
        print("✅ Correctly stopped at max steps")
    else:
        print("❌ Did not respect max_steps")

    # Test 6 - Unknown tool recovery
    data = run_test("Use a tool called magic_tool to solve 2+2")
    print_result("Unknown tool handling", data)

    print("\n" + "="*70)
    print("✅ All tests finished")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()