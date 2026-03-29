import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from client import ProcurementComplianceEnv
from models import ProcurementAction


BASE_URL = "http://127.0.0.1:8000"


def main():
    with ProcurementComplianceEnv(base_url=BASE_URL).sync() as env:
        result = env.reset()
        print("RESET RESULT")
        print(result.observation)
        print()

        action = ProcurementAction(
            policy_compliance="compliant",
            approval_decision="approve",
            risk_level="low",
            route_to="procurement_auto",
            missing_requirements=[],
        )

        step_result = env.step(action)
        print("STEP RESULT")
        print(step_result.observation)
        print(f"Reward: {step_result.reward}")
        print(f"Done: {step_result.done}")
        print()

        state = env.state()
        print("STATE")
        print(state)


if __name__ == "__main__":
    main()