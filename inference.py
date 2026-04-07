"""
Inference Script for Procurement Compliance Review Environment
===================================
MANDATORY
- Before submitting, ensure the following variables are defined:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.

- Uses OpenAI Client for all LLM calls
"""

import os
import json
import requests
from openai import OpenAI

API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"] 
MODEL_NAME = os.environ.get("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")

ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

SYSTEM_PROMPT = (
    "You are a procurement compliance reviewer for a company. "
    "You will receive a procurement request with details like department, item type, "
    "amount, vendor status, budget, and approval statuses. "
    "You must return a JSON object with exactly these fields: "
    "policy_compliance (string: compliant, non_compliant, or partial), "
    "approval_decision (string: approved, denied, needs_review, or escalate), "
    "risk_level (string: low, medium, or high), "
    "route_to (list of strings, e.g. [manager, finance, security]), "
    "missing_requirements (list of strings, e.g. [manager approval, security review]). "
    "Rules: "
    "All purchases need manager approval. "
    "Purchases over 5000 USD need finance approval. "
    "Software and cloud services need security review. "
    "Unapproved vendors need vendor onboarding or procurement review. "
    "Over-budget requests need budget exception review. "
    "Return ONLY valid JSON. No explanations."
)


def reset_env(task_id=None):
    payload = {}
    if task_id:
        payload["task_id"] = task_id
    response = requests.post(f"{ENV_URL}/reset", json=payload)
    response.raise_for_status()
    return response.json()


def step_env(action):
    response = requests.post(f"{ENV_URL}/step", json=action)
    response.raise_for_status()
    return response.json()


def build_user_prompt(observation):
    return (
        f"Review this procurement request:\n"
        f"- Request ID: {observation['request_id']}\n"
        f"- Department: {observation['department']}\n"
        f"- Requestor Role: {observation['requestor_role']}\n"
        f"- Item Type: {observation['item_type']}\n"
        f"- Item Description: {observation['item_description']}\n"
        f"- Amount (USD): {observation['amount_usd']}\n"
        f"- Budget Remaining (USD): {observation['budget_remaining_usd']}\n"
        f"- Vendor Status: {observation['vendor_status']}\n"
        f"- Manager Approval: {observation['manager_approval']}\n"
        f"- Finance Approval: {observation['finance_approval']}\n"
        f"- Security Review: {observation['security_review']}\n"
        f"- Urgency: {observation['urgency']}\n"
        f"- Policy Notes: {observation['policy_notes']}\n"
        f"\nReturn your compliance decision as a JSON object."
    )


def parse_llm_response(response_text):
    try:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "policy_compliance": "non_compliant",
            "approval_decision": "needs_review",
            "risk_level": "medium",
            "route_to": ["manager"],
            "missing_requirements": ["unable to parse LLM response"],
        }


def main():
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )

    observation = reset_env()

    print("[START]")
    print(json.dumps({
        "task_id": observation.get("request_id", "unknown"),
        "difficulty": observation.get("difficulty", "unknown"),
    }))

    user_prompt = build_user_prompt(observation)

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

    action = parse_llm_response(response_text)

    print("[STEP]")
    print(json.dumps({
        "action": action,
    }))

    result = step_env(action)
    reward = result.get("reward", 0.0)
    done = result.get("done", False)

    print("[END]")
    print(json.dumps({
        "reward": reward,
        "done": done,
        "message": result.get("message", ""),
    }))


if __name__ == "__main__":
    main()