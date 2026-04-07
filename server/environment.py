import json
import random
import uuid
from pathlib import Path
from typing import Any, Dict, List

from models import ProcurementAction, ProcurementObservation, ProcurementState


class ProcurementComplianceEnvironment:
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self.tasks = self._load_tasks()
        self.current_task: Dict[str, Any] | None = None
        self._state = ProcurementState()
        self._completed = False

    def _load_tasks(self) -> List[Dict[str, Any]]:
        data_path = Path(__file__).resolve().parent.parent / "data" / "tasks.json"
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def reset(self, seed=None, episode_id=None, task_id=None, **kwargs) -> ProcurementObservation:
        if seed is not None:
            random.seed(seed)

        if task_id is not None:
            matching_tasks = [task for task in self.tasks if task["id"] == task_id]
            if not matching_tasks:
                raise ValueError(f"Task ID not found: {task_id}")
            self.current_task = matching_tasks[0]
        else:
            self.current_task = random.choice(self.tasks)

        expected = self.current_task["expected_output"]

        self._state = ProcurementState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            current_task_id=self.current_task["id"],
            difficulty=self.current_task["difficulty"],
            expected_policy_compliance=expected["policy_compliance"],
            expected_approval_decision=expected["approval_decision"],
            expected_risk_level=expected["risk_level"],
            expected_route_to=expected["route_to"],
            expected_missing_requirements=expected["missing_requirements"],
            score_so_far=0.0,
            completed=False,
        )
        self._completed = False

        request = self.current_task["request"]

        return ProcurementObservation(
            done=False,
            reward=None,
            request_id=request["request_id"],
            department=request["department"],
            requestor_role=request["requestor_role"],
            item_type=request["item_type"],
            item_description=request["item_description"],
            amount_usd=request["amount_usd"],
            budget_remaining_usd=request["budget_remaining_usd"],
            vendor_status=request["vendor_status"],
            manager_approval=request["manager_approval"],
            finance_approval=request["finance_approval"],
            security_review=request["security_review"],
            urgency=request["urgency"],
            policy_notes=request["policy_notes"],
            difficulty=self.current_task["difficulty"],
            allowed_actions=["submit_decision"],
            message="Review this procurement request and submit a compliance decision."
        )

    def step(self, action: ProcurementAction, timeout_s=None, **kwargs) -> ProcurementObservation:
        if self.current_task is None:
            raise ValueError("Environment has not been reset. Call reset() first.")

        if self._completed:
            raise ValueError("Episode already completed. Call reset() to start a new episode.")

        self._state.step_count += 1

        expected = self.current_task["expected_output"]
        reward = self._grade_action(action, expected)

        self._state.score_so_far = reward
        self._state.completed = True
        self._completed = True

        request = self.current_task["request"]

        return ProcurementObservation(
            done=True,
            reward=reward,
            request_id=request["request_id"],
            department=request["department"],
            requestor_role=request["requestor_role"],
            item_type=request["item_type"],
            item_description=request["item_description"],
            amount_usd=request["amount_usd"],
            budget_remaining_usd=request["budget_remaining_usd"],
            vendor_status=request["vendor_status"],
            manager_approval=request["manager_approval"],
            finance_approval=request["finance_approval"],
            security_review=request["security_review"],
            urgency=request["urgency"],
            policy_notes=request["policy_notes"],
            difficulty=self.current_task["difficulty"],
            allowed_actions=["submit_decision"],
            message=f"Decision submitted. Final score: {reward:.2f}"
        )

    def state(self) -> ProcurementState:
        return self._state

    def _grade_action(self, action: ProcurementAction, expected: Dict[str, Any]) -> float:
        score = 0.0

        if action.policy_compliance == expected["policy_compliance"]:
            score += 0.25

        if action.approval_decision == expected["approval_decision"]:
            score += 0.25

        if action.risk_level == expected["risk_level"]:
            score += 0.15

        if action.route_to == expected["route_to"]:
            score += 0.20

        expected_missing = set(expected["missing_requirements"])
        submitted_missing = set(action.missing_requirements)

        if len(expected_missing) == 0 and len(submitted_missing) == 0:
            score += 0.15
        elif len(expected_missing) > 0:
            overlap = len(expected_missing.intersection(submitted_missing))
            score += 0.15 * (overlap / len(expected_missing))

        score = round(score, 4)
        score = max(0.01, min(0.99, score))
        return score   