import requests
import json

ENV_URL = "http://localhost:7860"

TASKS = {
    "easy_001": {
        "policy_compliance": "compliant",
        "approval_decision": "approved",
        "risk_level": "low",
        "route_to": [],
        "missing_requirements": []
    },
    "easy_002": {
        "policy_compliance": "partial",
        "approval_decision": "needs_review",
        "risk_level": "low",
        "route_to": ["manager"],
        "missing_requirements": ["manager_approval"]
    },
    "easy_003": {
        "policy_compliance": "compliant",
        "approval_decision": "approved",
        "risk_level": "low",
        "route_to": [],
        "missing_requirements": []
    },
    "easy_004": {
        "policy_compliance": "compliant",
        "approval_decision": "approved",
        "risk_level": "low",
        "route_to": [],
        "missing_requirements": []
    },
    "medium_001": {
        "policy_compliance": "partial",
        "approval_decision": "needs_review",
        "risk_level": "medium",
        "route_to": ["finance"],
        "missing_requirements": ["finance_approval"]
    },
    "medium_002": {
        "policy_compliance": "non_compliant",
        "approval_decision": "needs_review",
        "risk_level": "medium",
        "route_to": ["procurement"],
        "missing_requirements": ["vendor_onboarding"]
    },
    "medium_003": {
        "policy_compliance": "partial",
        "approval_decision": "needs_review",
        "risk_level": "low",
        "route_to": ["security"],
        "missing_requirements": ["security_review"]
    },
    "medium_004": {
        "policy_compliance": "non_compliant",
        "approval_decision": "needs_review",
        "risk_level": "high",
        "route_to": ["finance"],
        "missing_requirements": ["finance_approval"]
    },
    "hard_001": {
        "policy_compliance": "non_compliant",
        "approval_decision": "escalate",
        "risk_level": "high",
        "route_to": ["manager", "finance", "procurement"],
        "missing_requirements": ["manager_approval", "finance_approval", "vendor_onboarding", "budget_exception"]
    },
    "hard_002": {
        "policy_compliance": "non_compliant",
        "approval_decision": "escalate",
        "risk_level": "high",
        "route_to": ["security", "finance"],
        "missing_requirements": ["finance_approval", "security_review"]
    },
    "hard_003": {
        "policy_compliance": "non_compliant",
        "approval_decision": "escalate",
        "risk_level": "high",
        "route_to": ["manager", "finance", "security", "procurement"],
        "missing_requirements": ["manager_approval", "finance_approval", "security_review", "vendor_onboarding", "budget_exception"]
    },
    "hard_004": {
        "policy_compliance": "non_compliant",
        "approval_decision": "escalate",
        "risk_level": "high",
        "route_to": ["finance", "security", "procurement"],
        "missing_requirements": ["finance_approval", "security_review", "vendor_onboarding", "budget_exception"]
    },
}


def main():
    print("=" * 60)
    print("BASELINE GRADING TEST - ALL 12 TASKS")
    print("=" * 60)

    results = []

    for task_id, perfect_action in TASKS.items():
        reset_resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
        if reset_resp.status_code != 200:
            print(f"  X {task_id}: RESET FAILED ({reset_resp.status_code})")
            results.append({"task_id": task_id, "reward": 0, "status": "RESET_FAIL"})
            continue

        step_resp = requests.post(f"{ENV_URL}/step", json=perfect_action)
        if step_resp.status_code != 200:
            print(f"  X {task_id}: STEP FAILED ({step_resp.status_code})")
            results.append({"task_id": task_id, "reward": 0, "status": "STEP_FAIL"})
            continue

        data = step_resp.json()
        reward = data.get("reward", 0)
        results.append({"task_id": task_id, "reward": reward, "status": "OK"})

    print()
    print("-" * 45)
    print(f"{'Task ID':<15} {'Score':<10} {'Status':<10}")
    print("-" * 45)

    for r in results:
        if r["reward"] > 0.9:
            icon = "PASS"
        elif r["reward"] > 0.5:
            icon = "PARTIAL"
        else:
            icon = "FAIL"
        print(f"  {r['task_id']:<13} {r['reward']:<10.4f} {icon}")

    scored = [r for r in results if r["status"] == "OK"]
    avg = sum(r["reward"] for r in scored) / len(scored) if scored else 0

    print("-" * 45)
    print(f"Tasks scored:   {len(scored)} / {len(results)}")
    print(f"Average reward: {avg:.4f}")
    print(f"All > 0.0?      {'YES' if all(r['reward'] > 0 for r in scored) else 'NO'}")
    print(f"All < 1.0?      {'YES' if all(r['reward'] < 1 for r in scored) else 'NO'}")
    print(f"All in (0,1)?   {'YES' if all(0 < r['reward'] < 1 for r in scored) else 'NO'}")
    print("=" * 60)

    if len(scored) >= 3 and all(0 < r["reward"] < 1 for r in scored):
        print("PASS: At least 3 tasks with scores strictly in (0, 1)")
    else:
        print("FAIL: Does not meet validation requirements")


if __name__ == "__main__":
    main()
