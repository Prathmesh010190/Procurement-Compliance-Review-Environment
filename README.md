---
title: Procurement Compliance Review Environment
emoji: 📋
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# Procurement Compliance Review Environment

A real-world OpenEnv environment that simulates enterprise procurement compliance review. AI agents must review internal purchase requests and make structured compliance decisions based on organizational policy rules.

## Motivation

Procurement and compliance teams in organizations routinely review employee purchase requests to determine whether they satisfy internal policy, require additional approvals, or must be routed to finance, security, or vendor onboarding teams.

This environment models that real-world workflow as a structured decision-making task for AI agents. Unlike toy tasks, this benchmark reflects an actual enterprise process that thousands of companies perform daily — making it immediately useful for training and evaluating AI agents in business operations contexts.

## How It Works

Agent receives procurement request → Reviews against policy rules → Submits structured decision → Gets scored

Each episode contains a single procurement request. The agent must review the request details (department, amount, vendor status, existing approvals) against company procurement policies and return a complete structured compliance decision.

This is a single-step environment because procurement intake review is naturally a one-shot decision task based on the submitted request contents.

## Environment API

The environment implements the standard OpenEnv interface:

| Endpoint | Method | Description |
|----------|--------|------------|
| `/reset` | POST | Start a new episode with a random or specific task |
| `/step`  | POST | Submit a compliance decision and receive a score |
| `/state` | GET  | Get current episode state |
| `/tasks` | GET  | List all available task IDs |
| `/health`| GET  | Health check |
| `/docs`  | GET  | Interactive API documentation |

## Reset Request

```json
{
  "task_id": "easy_001",
  "seed": null,
  "episode_id": null
}
```

## Step Request (Action)

```json
{
  "policy_compliance": "partial",
  "approval_decision": "needs_review",
  "risk_level": "medium",
  "route_to": ["finance", "security"],
  "missing_requirements": ["finance_approval", "security_review"]
}
```

## Observation Space

The agent receives a structured procurement request containing:

| Field | Type | Description |
|------|------|------------|
| `request_id` | string | Unique request identifier |
| `department` | string | Requesting department (Engineering, HR, Marketing, etc.) |
| `requestor_role` | string | Role of the person making the request |
| `item_type` | string | Category: software, hardware, office_supplies, consulting, cloud_service, training |
| `item_description` | string | Detailed description of the item or service |
| `amount_usd` | float | Purchase amount in USD |
| `budget_remaining_usd` | float | Remaining department budget in USD |
| `vendor_status` | string | Vendor approval status: approved, unapproved, or new |
| `manager_approval` | bool | Whether manager has approved |
| `finance_approval` | bool | Whether finance has approved |
| `security_review` | bool | Whether security review is complete |
| `urgency` | string | Request urgency: low, normal, medium, high, urgent |
| `policy_notes` | string | Relevant policy rules for this request |
| `difficulty` | string | Task difficulty: easy, medium, or hard |
| `done` | bool | Whether the episode is complete |
| `reward` | float/null | Score (null on reset, 0.01–0.98 after step) |

## Setup Instructions

### Local Python Setup

```bash
git clone https://github.com/Prathmesh010190/Procurement-Compliance-Review-Environment.git
cd Procurement-Compliance-Review-Environment

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn server.app:app --host 0.0.0.0 --port 7860
```

Then open: http://localhost:7860/docs

---

### Docker Setup

```bash
docker build -t procurement-openenv .
docker run -p 7860:7860 procurement-openenv
```

---

### Run Baseline (Perfect Answers)

```bash
python scripts/baseline_inference.py
```

---

## Run LLM Inference

Ensure your API key is set correctly before running inference.

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export API_KEY="your_api_key_here"
export MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
export ENV_URL="http://localhost:7860"

python inference.py
```

---

## Validate Environment

```bash
pip install openenv-core
openenv validate
```

---

## Pre-Submission Validation

```bash
bash validate-submission.sh https://prathmesh1243-procurement-compliance-review-environment.hf.space .
```