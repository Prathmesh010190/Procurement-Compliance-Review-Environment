import json
import random
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from models import ProcurementAction, ProcurementObservation, ProcurementState


class ProcurementComplianceEnvironment:
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self.tasks = self._load_tasks()
        self.current_task: Optional[Dict[str, Any]] = None
        self._state = ProcurementState()
        self._completed = False

    def _load_tasks(self) -> List[Dict[str, Any]]:
        data_path = Path(__file__).resolve().parent.parent / "data" / "tasks.json"
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_task_ids(self) -> List[str]:
        """Return all available task IDs — used by validators to discover tasks."""
        return [task["id"] for task in self.tasks]

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
            message="Review this procurement request and submit a compliance decision.",
        )

    def step(self, action: ProcurementAction, timeout_s=None, **kwargs) -> ProcurementObservation:
        if self.current_task is None:
            raise ValueError("Environment has not been reset. Call reset() first.")

        if self._completed:
            raise ValueError("Episode already completed. Call reset() to start a new episode.")

        self._state.step_count += 1

        expected = self.current_task["expected_output"]

        # Wrap grading in try/except so it NEVER crashes
        try:
            reward = self._grade_action(action, expected)
        except Exception:
            reward = 0.01  # Safe fallback — strictly between 0 and 1

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
            message=f"Decision submitted. Final score: {reward:.4f}",
        )

    def state(self) -> ProcurementState:
        return self._state

    # ------------------------------------------------------------------
    # GRADER — deterministic, weighted partial credit
    # ------------------------------------------------------------------
    def _grade_action(self, action: ProcurementAction, expected: Dict[str, Any]) -> float:
        score = 0.0

        # --- 1. policy_compliance (weight 0.25) ---
        try:
            act_val = str(action.policy_compliance or "").strip().lower()
            exp_val = str(expected.get("policy_compliance", "")).strip().lower()
            if act_val and exp_val and act_val == exp_val:
                score += 0.25
        except Exception:
            pass

        # --- 2. approval_decision (weight 0.25) ---
        try:
            act_val = str(action.approval_decision or "").strip().lower()
            exp_val = str(expected.get("approval_decision", "")).strip().lower()
            if act_val and exp_val and act_val == exp_val:
                score += 0.25
        except Exception:
            pass

        # --- 3. risk_level (weight 0.15) ---
        try:
            act_val = str(action.risk_level or "").strip().lower()
            exp_val = str(expected.get("risk_level", "")).strip().lower()
            if act_val and exp_val and act_val == exp_val:
                score += 0.15
        except Exception:
            pass

        # --- 4. route_to (weight 0.20) — set-based partial credit ---
        try:
            exp_route = set(expected.get("route_to") or [])
            act_route = set(action.route_to or [])
            if not exp_route and not act_route:
                score += 0.20
            elif exp_route:
                overlap = len(exp_route.intersection(act_route))
                denominator = max(len(exp_route), len(act_route))
                if denominator > 0:
                    score += 0.20 * (overlap / denominator)
        except Exception:
            pass

        # --- 5. missing_requirements (weight 0.15) — set overlap ---
        try:
            exp_missing = set(expected.get("missing_requirements") or [])
            act_missing = set(action.missing_requirements or [])
            if not exp_missing and not act_missing:
                score += 0.15
            elif exp_missing:
                overlap = len(exp_missing.intersection(act_missing))
                score += 0.15 * (overlap / len(exp_missing))
        except Exception:
            pass

        # ----------------------------------------------------------
        # CLAMP: strictly between 0 and 1  (never 0.0, never 1.0)
        # ----------------------------------------------------------
        score = round(score, 4)
        score = max(0.01, min(0.99, score))
        return score