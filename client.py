from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient

from models import ProcurementAction, ProcurementObservation, ProcurementState


class ProcurementComplianceEnv(
    EnvClient[ProcurementAction, ProcurementObservation, ProcurementState]
):
    def _step_payload(self, action: ProcurementAction) -> dict:
        return {
            "policy_compliance": action.policy_compliance,
            "approval_decision": action.approval_decision,
            "risk_level": action.risk_level,
            "route_to": action.route_to,
            "missing_requirements": action.missing_requirements,
        }

    def _parse_result(self, payload: dict) -> StepResult:
        observation_data = payload.get("observation", {})

        observation = ProcurementObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            request_id=observation_data.get("request_id", ""),
            department=observation_data.get("department", ""),
            requestor_role=observation_data.get("requestor_role", ""),
            item_type=observation_data.get("item_type", ""),
            item_description=observation_data.get("item_description", ""),
            amount_usd=observation_data.get("amount_usd", 0.0),
            budget_remaining_usd=observation_data.get("budget_remaining_usd", 0.0),
            vendor_status=observation_data.get("vendor_status", ""),
            manager_approval=observation_data.get("manager_approval", False),
            finance_approval=observation_data.get("finance_approval", False),
            security_review=observation_data.get("security_review", False),
            urgency=observation_data.get("urgency", ""),
            policy_notes=observation_data.get("policy_notes", ""),
            difficulty=observation_data.get("difficulty", ""),
            allowed_actions=observation_data.get("allowed_actions", []),
            message=observation_data.get("message", ""),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> ProcurementState:
        return ProcurementState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            current_task_id=payload.get("current_task_id", ""),
            difficulty=payload.get("difficulty", ""),
            expected_policy_compliance=payload.get("expected_policy_compliance", ""),
            expected_approval_decision=payload.get("expected_approval_decision", ""),
            expected_risk_level=payload.get("expected_risk_level", ""),
            expected_route_to=payload.get("expected_route_to", ""),
            expected_missing_requirements=payload.get("expected_missing_requirements", []),
            score_so_far=payload.get("score_so_far", 0.0),
            completed=payload.get("completed", False),
        )