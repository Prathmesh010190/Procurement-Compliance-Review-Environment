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

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3")

ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

SYSTEM_PROMPT = """
You are a procurement compliance reviewer for a company.
You will receive a procurement request with details like department, item type,
amount, vendor status, budget, and approval statuses.

You must return a JSON object with exactly these fields:
- policy_compliance: string ("compliant", "non_compliant", or "partial")
- approval_decision: string ("approved", "denied", or "needs_review")
- risk_level: string ("low", "medium", or "high")
- route_to: list of strings (e.g. ["manager", "finance", "security"])
- missing_requirements: list of strings (e.g. ["manager approval", "security review"])

Rules:
- All purchases need manager approval
- Purchases over \$5000 need finance approval
- Software/cloud services need security review
- Unapproved vendors need vendor onboarding/procurement review
- Over-budget requests need budget exception review

Return ONLY valid JSON. No explanations.
""".strip()


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
    return f"""
Review this procurement request:

- Request ID: {observation['request_id']}
- Department: {observation['department']}
- Requestor Role: {observation['requestor_role']}
- Item Type: {observation['item_type']}
- Item Description: {observation['item_description']}
- Amount (USD): {observation['amount_usd']}
- Budget Remaining (USD): {observation['budget_remaining_usd']}
- Vendor Status: {observation['vendor_status']}
- Manager Approval: {observation['manager_approval']}
- Finance Approval: {observation['finance_approval']}
- Security Review: {observation['security_review']}
- Urgency: {observation['urgency']}
- Policy Notes: {observation['policy_notes']}

Return your compliance decision as a JSON object.
""".strip()


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
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    observation = reset_env()
    print(f"Task: {observation.get('request_id', 'unknown')}")
    print(f"Difficulty: {observation.get('difficulty', 'unknown')}")

    user_prompt = build_user_prompt(observation)

    try:
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
        print(f"LLM Response: {response_text}")
    except Exception as e:
        print(f"LLM call failed: {e}")
        response_text = ""

    action = parse_llm_response(response_text)
    print(f"Parsed Action: {json.dumps(action, indent=2)}")

    result = step_env(action)
    reward = result.get("reward", 0.0)
    print(f"Reward: {reward}")
    print(f"Done: {result.get('done', False)}")
    print(f"Message: {result.get('message', '')}")


if __name__ == "__main__":
    main()