"""
Inference Script for Procurement Compliance Review Environment
===================================
MANDATORY
- Before submitting, ensure the following variables are defined:
    API_BASE_URL   The API endpoint for the LLM (injected by hackathon platform).
    API_KEY        The API key for the LLM proxy (injected by hackathon platform).
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face token (optional fallback for API_KEY).

- Uses OpenAI Client for all LLM calls
"""

import os
import json
import requests
from typing import List, Optional

from openai import OpenAI

# ---------- MANDATORY: use platform-injected env vars ----------
API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.environ.get("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")
BENCHMARK = "procurement-compliance"
MAX_STEPS = 1


SYSTEM_PROMPT = (
    "You are a procurement compliance reviewer for a company. "
    "You will receive a procurement request with details like department, item type, "
    "amount, vendor status, budget, and approval statuses. "
    "You must return a JSON object with exactly these fields: "
    "policy_compliance (string: compliant, non_compliant, or partial), "
    "approval_decision (string: approved, denied, needs_review, or escalate), "
    "risk_level (string: low, medium, or high), "
    "route_to (list of strings, e.g. [\"manager\", \"finance\", \"security\", \"procurement\"]), "
    "missing_requirements (list of strings, e.g. [\"manager_approval\", \"finance_approval\", "
    "\"security_review\", \"vendor_onboarding\", \"budget_exception\"]). "
    "Rules: "
    "1. All purchases need manager approval. "
    "2. Purchases over 5000 USD need finance approval. "
    "3. Software and cloud services need security review. "
    "4. Unapproved or new vendors need vendor onboarding (procurement review). "
    "5. Over-budget requests (amount > budget_remaining) need budget exception review. "
    "6. If all requirements met: compliant + approved + low risk. "
    "7. If one requirement missing: partial + needs_review. "
    "8. If multiple requirements missing or critical issues: non_compliant + escalate + high risk. "
    "Return ONLY valid JSON. No explanations."
)


# ──────────────────────────────────────────────
# STRUCTURED LOGGING — MANDATORY FORMAT
# ──────────────────────────────────────────────
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ──────────────────────────────────────────────
# ENVIRONMENT HELPERS
# ──────────────────────────────────────────────
def get_task_ids() -> List[str]:
    try:
        resp = requests.get(f"{ENV_URL}/tasks", timeout=10)
        resp.raise_for_status()
        return resp.json().get("task_ids", [])
    except Exception:
        return [
            "easy_001", "easy_002", "easy_003", "easy_004",
            "medium_001", "medium_002", "medium_003", "medium_004",
            "hard_001", "hard_002", "hard_003", "hard_004",
        ]


def reset_env(task_id: str) -> dict:
    resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def step_env(action: dict) -> dict:
    resp = requests.post(f"{ENV_URL}/step", json=action, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ──────────────────────────────────────────────
# LLM HELPERS
# ──────────────────────────────────────────────
def build_user_prompt(obs: dict) -> str:
    return (
        f"Review this procurement request:\n"
        f"- Request ID: {obs.get('request_id', 'N/A')}\n"
        f"- Department: {obs.get('department', 'N/A')}\n"
        f"- Requestor Role: {obs.get('requestor_role', 'N/A')}\n"
        f"- Item Type: {obs.get('item_type', 'N/A')}\n"
        f"- Item Description: {obs.get('item_description', 'N/A')}\n"
        f"- Amount (USD): {obs.get('amount_usd', 0)}\n"
        f"- Budget Remaining (USD): {obs.get('budget_remaining_usd', 0)}\n"
        f"- Vendor Status: {obs.get('vendor_status', 'N/A')}\n"
        f"- Manager Approval: {obs.get('manager_approval', False)}\n"
        f"- Finance Approval: {obs.get('finance_approval', False)}\n"
        f"- Security Review: {obs.get('security_review', False)}\n"
        f"- Urgency: {obs.get('urgency', 'N/A')}\n"
        f"- Policy Notes: {obs.get('policy_notes', 'N/A')}\n"
        f"\nReturn your compliance decision as a JSON object."
    )


def parse_llm_response(response_text: str) -> dict:
    try:
        cleaned = response_text.strip()
        if "```" in cleaned:
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines).strip()
        parsed = json.loads(cleaned)
        action = {
            "policy_compliance": str(parsed.get("policy_compliance", "non_compliant")).strip().lower(),
            "approval_decision": str(parsed.get("approval_decision", "needs_review")).strip().lower(),
            "risk_level": str(parsed.get("risk_level", "medium")).strip().lower(),
            "route_to": parsed.get("route_to", ["manager"]),
            "missing_requirements": parsed.get("missing_requirements", []),
        }
        if not isinstance(action["route_to"], list):
            action["route_to"] = [str(action["route_to"])]
        if not isinstance(action["missing_requirements"], list):
            action["missing_requirements"] = [str(action["missing_requirements"])]
        return action
    except Exception:
        return {
            "policy_compliance": "non_compliant",
            "approval_decision": "needs_review",
            "risk_level": "medium",
            "route_to": ["manager"],
            "missing_requirements": ["manager_approval"],
        }


def get_llm_action(client: OpenAI, obs: dict) -> dict:
    try:
        user_prompt = build_user_prompt(obs)
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        response_text = completion.choices[0].message.content or ""
        return parse_llm_response(response_text)
    except Exception:
        return {
            "policy_compliance": "non_compliant",
            "approval_decision": "needs_review",
            "risk_level": "medium",
            "route_to": ["manager"],
            "missing_requirements": ["manager_approval"],
        }


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    # MANDATORY: use injected API_BASE_URL and API_KEY
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )

    task_ids = get_task_ids()

    for task_id in task_ids:
        rewards: List[float] = []
        steps_taken = 0
        score = 0.0
        success = False

        log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

        try:
            obs = reset_env(task_id)
            action = get_llm_action(client, obs)
            action_str = f"submit_decision({action['approval_decision']})"

            result = step_env(action)
            reward = result.get("reward", 0.01)
            done = result.get("done", True)
            steps_taken = 1
            rewards.append(reward)

            log_step(step=1, action=action_str, reward=reward, done=done, error=None)

            score = reward
            success = score > 0.1

        except Exception as e:
            steps_taken = max(steps_taken, 1)
            if not rewards:
                rewards.append(0.0)
            score = 0.0
            success = False
            log_step(step=1, action="error", reward=0.0, done=True, error=str(e))

        finally:
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()