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

---

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

---

## 🚀 Setup Instructions

### 🔹 Local Python Setup

```bash
git clone https://github.com/Prathmesh010190/Procurement-Compliance-Review-Environment.git
cd Procurement-Compliance-Review-Environment

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn server.app:app --host 0.0.0.0 --port 7860
```

👉 Open API Docs: [http://localhost:7860/docs](http://localhost:7860/docs)

---

### 🐳 Docker Setup

```bash
docker build -t procurement-openenv .
docker run -p 7860:7860 procurement-openenv
```

---

### 🧠 Run Baseline (Perfect Answers)

```bash
python scripts/baseline_inference.py
```

---

## 🤖 Run LLM Inference

Ensure your API key is set correctly before running inference.

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export API_KEY="your_api_key_here"
export MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
export ENV_URL="http://localhost:7860"

python inference.py
```

---

## ✅ Validate Environment

```bash
pip install openenv-core
openenv validate
```

---

## 🧪 Pre-Submission Validation

```bash
bash validate-submission.sh https://prathmesh1243-procurement-compliance-review-environment.hf.space .
```

---

## 🌐 Deployment

| Resource | Link |
|----------|------|
| 🚀 Live App | [Open App](https://huggingface.co/spaces/Prathmesh1243) |
| 📄 API Docs | [Swagger UI](https://prathmesh1243-procurement-compliance-review-environment.hf.space/docs) |
| ❤️ Health Check | [Check Status](https://prathmesh1243-procurement-compliance-review-environment.hf.space/health) |
| 🤗 HF Space | https://huggingface.co/spaces/Prathmesh1243 |
| 💻 GitHub | https://github.com/Prathmesh010190 |

## Repository Structure

```text
.
├── Dockerfile                     # Docker image for HF Spaces deployment
├── README.md                     # This file
├── openenv.yaml                  # OpenEnv environment configuration
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Python dependencies
├── uv.lock                       # Dependency lock file
├── inference.py                  # LLM inference script (mandatory, uses OpenAI client)
├── models.py                     # Typed Pydantic models (Action, Observation, State)
├── client.py                     # HTTP client for the environment
├── validate-submission.sh        # Pre-submission validation script
├── .env.example                  # Example environment variables
├── .gitignore
├── data/
│   └── tasks.json                # 12 procurement review tasks (4 easy, 4 medium, 4 hard)
├── scripts/
│   ├── baseline_inference.py     # Rule-based baseline (deterministic, perfect answers)
│   └── test_client.py            # Client testing script
├── server/
│   ├── __init__.py
│   ├── app.py                   # FastAPI server with reset/step/state/tasks endpoints
│   └── environment.py           # Core environment logic and grading
└── tests/
    └── test_basic.py            # Basic environment tests
```

## Technical Details

### Typed Models

All models use Pydantic `BaseModel` for type safety and validation:

| Model | Purpose |
|------|--------|
| `ProcurementAction` | Agent's compliance decision (5 fields) |
| `ProcurementObservation` | Procurement request details + reward + done flag |
| `ProcurementState` | Episode tracking with expected values |

---

### Environment Design

- Single-step episodes reflecting real procurement intake review  
- Deterministic grading with weighted partial credit  
- Difficulty-aware scoring with complexity bonuses  
- Support for `task_id` parameter for reproducible evaluation  
- Concurrent session support  
- Case-insensitive string matching  
- Null-safe field handling with try/except guards  
- Set-based partial credit for list fields (`route_to`, `missing_requirements`)  

## Inference Script

- Uses OpenAI client for all LLM calls  
- Reads platform-injected environment variables: `API_BASE_URL`, `API_KEY`  
- Configurable `MODEL_NAME` with sensible default  
- Emits structured `[START]`, `[STEP]`, `[END]` stdout logs per hackathon spec  
- Loops through all 12 tasks  
- Includes fallback handling if LLM call fails  
- Runtime well under 20 minute limit  

---

## Why This Benchmark Is Useful

This environment tests whether an AI agent can:

1. **Apply enterprise policy logic** — correctly identify which rules apply to each request  
2. **Identify missing requirements** — determine what approvals or reviews are still needed  
3. **Choose appropriate decisions** — approve, deny, escalate, or route for review  
4. **Route to correct teams** — direct requests to the right internal stakeholders  
5. **Assess risk accurately** — evaluate the risk level based on violation severity  
6. **Produce structured outputs** — generate auditable, machine-readable compliance decisions  

These are realistic capabilities needed in internal operations AI systems used by procurement, finance, and compliance teams worldwide.

## Limitations and Future Work

- **Single-step episodes** — could be extended to multi-turn clarification workflows  
- **Static policies** — could add policy versioning and dynamic rule changes  
- **12 tasks** — could be expanded to a larger and more diverse benchmark set  
- **Text-only** — could include document attachment review (invoices, contracts)  
- **No vendor database** — could add realistic vendor lookup integration  
- **No temporal context** — could add purchase history and spending pattern analysis  