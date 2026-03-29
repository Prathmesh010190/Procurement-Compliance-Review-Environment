# Procurement-Compliance-Review-Environment# Procurement Compliance Review OpenEnv

A real-world OpenEnv environment for evaluating AI agents on procurement compliance review and approval routing.

## Problem Overview

Organizations process internal purchase requests for software, hardware, consulting, cloud services, and office equipment. Before approval, procurement and finance teams must verify whether requests comply with internal policy.

This environment simulates that workflow. An agent receives a procurement request and must determine:

- policy compliance status
- approval decision
- risk level
- routing destination
- missing approval or policy requirements

This is a realistic operational task used in companies, universities, nonprofits, and enterprise procurement teams.

---

## OpenEnv Interface

This environment supports the standard OpenEnv API:

- `reset()`
- `step(action)`
- `state()`

---

## Observation Space

The agent receives a structured procurement request with fields such as:

- `request_id`
- `department`
- `requestor_role`
- `item_type`
- `item_description`
- `amount_usd`
- `budget_remaining_usd`
- `vendor_status`
- `manager_approval`
- `finance_approval`
- `security_review`
- `urgency`
- `policy_notes`
- `difficulty`

---

## Action Space

The agent submits a structured decision with:

- `policy_compliance`
- `approval_decision`
- `risk_level`
- `route_to`
- `missing_requirements`

### Example action

```json
{
  "policy_compliance": "partial",
  "approval_decision": "needs_review",
  "risk_level": "medium",
  "route_to": "finance_queue",
  "missing_requirements": ["finance_approval"]
}

## Example Baseline Results

A rule-based baseline policy is included for deterministic evaluation.

Example output format:

```bash
BASELINE RESULTS
--------------------------------------------------
easy_001     | easy   | score=1.00
easy_002     | easy   | score=1.00
medium_001   | medium | score=1.00
medium_002   | medium | score=1.00
hard_001     | hard   | score=0.95
hard_002     | hard   | score=1.00
--------------------------------------------------
Average score: 0.992