import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from server.environment import ProcurementComplianceEnvironment
from models import ProcurementAction


def test_reset_and_step():
    env = ProcurementComplianceEnvironment()
    obs = env.reset(task_id="easy_001")
    assert obs.request_id == "REQ-001"

    action = ProcurementAction(
        policy_compliance="compliant",
        approval_decision="approve",
        risk_level="low",
        route_to="procurement_auto",
        missing_requirements=[],
    )

    result = env.step(action)
    assert result.done is True
    assert result.reward == 1.0