"""
Baseline inference script for Procurement Compliance Review Environment.
Uses hand-coded policy rules. No LLM needed.
Reproducible and deterministic.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from client import ProcurementComplianceEnv

ENV_URL = "http://localhost:7860"


def load_task_ids():
    tasks_path = Path(__file__).resolve().parent.parent / "data" / "tasks.json"
    with open(tasks_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    return [t["id"] for t in tasks]


def rule_based_decision(obs):
    amount = obs.get("amount_usd", 0)
    budget = obs.get("budget_remaining_usd", 0)
    vendor = obs.get("vendor_status", "")
    manager = obs.get("manager_approval", False)
    finance = obs.get("finance_approval", False)
    security = obs.get("security_review", False)
    item_type = obs.get("item_type", "").lower()

    route_to = []
    missing = []
    policy = "compliant"
    risk = "low"

    if not manager:
        route_to.append("manager")
        missing.append("manager approval")
        policy = "non_compliant"

    if amount > 5000 and not finance:
        route_to.append("finance")
        missing.append("finance approval")
        policy = "non_compliant"

    needs_security = item_type in ["software", "cloud service", "saas", "cloud_service"]
    if needs_security and not security:
        route_to.append("security")
        missing.append("security review")
        if policy == "compliant":
            policy = "partial"

    if vendor in ["unapproved", "new", "unknown"]:
        route_to.append("procurement")
        missing.append("vendor onboarding")
        if policy == "compliant":
            policy = "partial"

    if amount > budget:
        missing.append("budget exception approval")
        if policy == "compliant":
            policy = "partial"

    if amount > 10000:
        risk = "high"
    elif amount > 5000:
        risk = "medium"

    if len(missing) == 0:
        decision = "approved"
    elif len(missing) <= 2:
        decision = "needs_review"
    else:
        decision = "denied"

    return {
        "policy_compliance": policy,
        "approval_decision": decision,
        "risk_level": risk,
        "route_to": route_to,
        "missing_requirements": missing,
    }


def main():
    env = ProcurementComplianceEnv(base_url=ENV_URL)
    task_ids = load_task_ids()

    results = []

    for task_id in task_ids:
        obs = env.reset(task_id=task_id)
        action = rule_based_decision(obs)
        result = env.step(action)

        reward = result.get("reward", 0.0)
        difficulty = obs.get("difficulty", "unknown")

        print(f"{task_id:20s} {difficulty:8s} score={reward:.4f}")
        results.append({
            "task_id": task_id,
            "difficulty": difficulty,
            "score": reward,
        })

    avg = sum(r["score"] for r in results) / len(results) if results else 0
    print(f"\n{'Overall average':20s} {'':8s} score={avg:.4f}")

    for level in ["easy", "medium", "hard"]:
        level_results = [r for r in results if r["difficulty"] == level]
        if level_results:
            level_avg = sum(r["score"] for r in level_results) / len(level_results)
            print(f"{level:20s} {'':8s} avg={level_avg:.4f}")


if __name__ == "__main__":
    main()