import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from client import ProcurementComplianceEnv
from models import ProcurementAction


BASE_URL = "http://127.0.0.1:8000"
TASKS_PATH = ROOT_DIR / "data" / "tasks.json"


def load_tasks():
    with open(TASKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def predict_action(observation):
    missing_requirements = []

    amount = observation.amount_usd
    budget = observation.budget_remaining_usd
    vendor_status = observation.vendor_status
    manager_approval = observation.manager_approval
    finance_approval = observation.finance_approval
    security_review = observation.security_review
    item_type = observation.item_type

    if not manager_approval:
        missing_requirements.append("manager_approval")

    if amount > 5000 and not finance_approval:
        missing_requirements.append("finance_approval")

    if vendor_status != "approved":
        missing_requirements.append("vendor_onboarding")

    if item_type in ["software", "cloud_service"] and not security_review:
        missing_requirements.append("security_review")

    if amount > budget:
        missing_requirements.append("budget_exception")

    if len(missing_requirements) == 0:
        return ProcurementAction(
            policy_compliance="compliant",
            approval_decision="approve",
            risk_level="low",
            route_to="procurement_auto",
            missing_requirements=[],
        )

    if len(missing_requirements) == 1:
        missing_item = missing_requirements[0]

        if missing_item == "manager_approval":
            return ProcurementAction(
                policy_compliance="partial",
                approval_decision="needs_review",
                risk_level="low",
                route_to="manager_queue",
                missing_requirements=missing_requirements,
            )

        if missing_item == "finance_approval":
            return ProcurementAction(
                policy_compliance="partial",
                approval_decision="needs_review",
                risk_level="medium",
                route_to="finance_queue",
                missing_requirements=missing_requirements,
            )

        if missing_item == "vendor_onboarding":
            return ProcurementAction(
                policy_compliance="non_compliant",
                approval_decision="needs_review",
                risk_level="medium",
                route_to="procurement_queue",
                missing_requirements=missing_requirements,
            )

        if missing_item == "security_review":
            return ProcurementAction(
                policy_compliance="non_compliant",
                approval_decision="needs_review",
                risk_level="medium",
                route_to="security_queue",
                missing_requirements=missing_requirements,
            )

        if missing_item == "budget_exception":
            return ProcurementAction(
                policy_compliance="non_compliant",
                approval_decision="needs_review",
                risk_level="medium",
                route_to="finance_queue",
                missing_requirements=missing_requirements,
            )

    if "security_review" in missing_requirements and "finance_approval" in missing_requirements:
        return ProcurementAction(
            policy_compliance="non_compliant",
            approval_decision="escalate",
            risk_level="high",
            route_to="security_finance_queue",
            missing_requirements=sorted(missing_requirements),
        )

    return ProcurementAction(
        policy_compliance="non_compliant",
        approval_decision="escalate",
        risk_level="high",
        route_to="procurement_queue",
        missing_requirements=sorted(missing_requirements),
    )


def main():
    tasks = load_tasks()
    scores = []

    with ProcurementComplianceEnv(base_url=BASE_URL).sync() as env:
        for task in tasks:
            result = env.reset(task_id=task["id"])
            action = predict_action(result.observation)
            step_result = env.step(action)
            score = step_result.reward if step_result.reward is not None else 0.0
            scores.append((task["id"], task["difficulty"], score))

    print("BASELINE RESULTS")
    print("-" * 50)

    total_score = 0.0
    for task_id, difficulty, score in scores:
        print(f"{task_id:12} | {difficulty:6} | score={score:.2f}")
        total_score += score

    average_score = total_score / len(scores) if scores else 0.0
    print("-" * 50)
    print(f"Average score: {average_score:.3f}")


if __name__ == "__main__":
    main()