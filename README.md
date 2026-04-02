---
title: Procurement Compliance Review Environment
emoji: 📋
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Procurement Compliance Review Environment

A real-world OpenEnv environment that simulates enterprise procurement compliance review. AI agents must review internal purchase requests and make structured compliance decisions.

## Motivation

Procurement and compliance teams in organizations routinely review employee purchase requests to determine whether they satisfy internal policy, require additional approvals, or must be routed to finance, security, or vendor onboarding teams.

This environment models that real-world workflow as a structured decision-making task for AI agents. Unlike toy tasks, this benchmark reflects an actual enterprise process that thousands of companies perform daily.

## How It Works

Each episode contains a single procurement request. The agent must review the request details and return a complete structured compliance decision.

Agent receives procurement request → Reviews against policy rules → Submits structured decision → Gets scored

This is a single-step environment because procurement intake review is naturally a one-shot decision task based on the submitted request contents.

---

## Environment API

The environment implements the standard OpenEnv interface:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Start a new episode with a random or specific task |
| `/step` | POST | Submit a compliance decision and receive a score |
| `/state` | GET | Get current episode state |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

---

## Observation Space

The agent receives a structured procurement request containing:

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique request identifier |
| `department` | string | Requesting department |
| `requestor_role` | string | Role of the person making the request |
| `item_type` | string | Category of purchase |
| `item_description` | string | Detailed description of the item |
| `amount_usd` | float | Purchase amount in USD |
| `budget_remaining_usd` | float | Remaining department budget |
| `vendor_status` | string | Vendor approval status |
| `manager_approval` | bool | Whether manager has approved |
| `finance_approval` | bool | Whether finance has approved |
| `security_review` | bool | Whether security review is complete |
| `urgency` | string | Request urgency level |
| `policy_notes` | string | Relevant policy information |
| `difficulty` | string | Task difficulty (easy/medium/hard) |

---

## Action Space

The agent submits a structured compliance decision:

| Field | Type | Description |
|-------|------|-------------|
| `policy_compliance` | string | "compliant", "non_compliant", or "partial" |
| `approval_decision` | string | "approved", "denied", "needs_review", or "escalate" |
| `risk_level` | string | "low", "medium", or "high" |
| `route_to` | string or list | Routing destination(s) for the request |
| `missing_requirements` | list | List of missing approvals or requirements |

### Example Action

```json
{
  "policy_compliance": "partial",
  "approval_decision": "needs_review",
  "risk_level": "medium",
  "route_to": ["finance", "security"],
  "missing_requirements": ["finance approval", "security review"]
}
```

---

## Procurement Policy Rules

The environment enforces these enterprise procurement policies:

| Rule | Condition |
|------|-----------|
| Manager approval | All purchases require manager approval |
| Finance approval | Purchases over $5,000 require finance approval |
| Security review | Software and cloud services require security review |
| Vendor onboarding | Unapproved or new vendors require procurement review |
| Budget exception | Over-budget requests require budget exception approval |

---

## Reward Design

The reward is a deterministic score from 0.0 to 1.0 with weighted partial credit:

| Field | Weight | Description |
|-------|--------|-------------|
| Policy compliance | 0.25 | Correct compliance classification |
| Approval decision | 0.25 | Correct approval routing decision |
| Risk level | 0.15 | Correct risk assessment |
| Route to | 0.20 | Correct team routing |
| Missing requirements | 0.15 | Overlap with expected missing items |

Partial credit is awarded for `missing_requirements` based on the overlap between predicted and expected items, making the reward informative rather than purely binary.

---

## Tasks

12 tasks across 3 difficulty levels:

### Easy (4 tasks)
Simple requests with one or two straightforward policy checks. Examples include standard office supply purchases and approved software subscriptions.

### Medium (4 tasks)
Requests involving multiple concurrent policy conditions, such as high-value purchases requiring both finance approval and security review.

### Hard (4 tasks)
Requests with several interacting constraints including over-budget purchases from unapproved vendors requiring multiple review routes and missing prerequisites.

---

## Baseline Results

Rule-based baseline using hand-coded procurement policy logic. No LLM required.

| Task | Difficulty | Score |
|------|------------|-------|
| easy_001 | easy | 0.5500 |
| easy_002 | easy | 0.4000 |
| easy_003 | easy | 1.0000 |
| easy_004 | easy | 1.0000 |
| medium_001 | medium | 0.4000 |
| medium_002 | medium | 0.2500 |
| medium_003 | medium | 1.0000 |
| medium_004 | medium | 1.0000 |
| hard_001 | hard | 0.4000 |
| hard_002 | hard | 0.4000 |
| hard_003 | hard | 1.0000 |
| hard_004 | hard | 1.0000 |

| Level | Average Score |
|-------|---------------|
| Easy | 0.7375 |
| Medium | 0.6625 |
| Hard | 0.7000 |
| **Overall** | **0.7000** |

The baseline is deterministic and reproducible. An LLM-based agent using `inference.py` is expected to score higher by understanding nuanced policy interactions.

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)

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

### Docker Setup

```bash
docker build -t procurement-openenv .
docker run -p 7860:7860 procurement-openenv
```

### Run Baseline

```bash
python scripts/baseline_inference.py
```

### Run LLM Inference

```bash
export HF_TOKEN="your_huggingface_token"
export MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
export API_BASE_URL="https://router.huggingface.co/v1"
python inference.py
```

### Validate Environment

```bash
pip install openenv-core
openenv validate
```

---

## Deployment

This environment is deployed as a Docker-based Hugging Face Space.

| Resource | URL |
|----------|-----|
| Live App | https://prathmesh1243-procurement-compliance-review-environment.hf.space |
| API Docs | https://prathmesh1243-procurement-compliance-review-environment.hf.space/docs |
| Health Check | https://prathmesh1243-procurement-compliance-review-environment.hf.space/health |
| HF Space | https://huggingface.co/spaces/Prathmesh1243/Procurement_Compliance_Review_Environment |
| GitHub | https://github.com/Prathmesh010190/Procurement-Compliance-Review-Environment |

---

## Repository Structure

```text
.
├── Dockerfile                    # Docker image for HF Spaces deployment
├── README.md                     # This file
├── openenv.yaml                  # OpenEnv configuration
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Python dependencies
├── uv.lock                       # Dependency lock file
├── models.py                     # Typed Pydantic models (Action, Observation, State)
├── client.py                     # HTTP client for the environment
├── inference.py                  # LLM inference script (mandatory, uses OpenAI client)
├── data/
│   └── tasks.json                # 12 procurement review tasks
├── scripts/
│   ├── baseline_inference.py     # Rule-based baseline (deterministic)
│   └── test_client.py            # Client testing script
├── server/
│   ├── __init__.py
│   ├── app.py                    # FastAPI server with reset/step/state endpoints
│   └── environment.py            # Core environment logic and grading
├── tests/
│   └── test_basic.py             # Basic environment tests
├── .env.example                  # Example environment variables
└── .gitignore
```

---

## Technical Details

### Models

All models use Pydantic BaseModel for type safety and validation:

- **ProcurementAction**: Agent's compliance decision
- **ProcurementObservation**: Procurement request details + reward
- **ProcurementState**: Episode tracking and expected values

### Environment Design

- Single-step episodes reflecting real procurement intake review
- Deterministic grading with weighted partial credit
- Support for `task_id` parameter for reproducible evaluation
- Concurrent session support

### Inference Script

- Uses OpenAI client for LLM calls
- Reads environment variables: `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN`
- Emits structured `[START]`, `[STEP]`, `[END]` stdout logs
- Includes fallback handling if LLM call fails

---

## Why This Benchmark Is Useful

This environment tests whether an AI agent can:

- Apply enterprise policy logic correctly
- Identify missing procurement requirements
- Choose appropriate approval decisions
- Route requests to the correct internal teams
- Produce structured, auditable compliance outputs

These are realistic capabilities needed in internal operations AI systems used by procurement, finance, and compliance teams worldwide.

---

## Limitations and Future Work

- **Single-step episodes**: Could be extended to multi-turn clarification workflows
- **Static policies**: Could add policy versioning and dynamic rule changes
- **12 tasks**: Could be expanded to a larger benchmark set
- **Text-only**: Could include document attachment review
- **No vendor database**: Could add realistic vendor lookup integration