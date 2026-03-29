---
title: Procurement Compliance Review Environment
emoji: 📋
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

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
## Baseline Results

Rule-based baseline using hand-coded procurement policy logic.

| Task | Difficulty | Score |
|------|-----------|-------|
| easy_001 | easy | 0.5500 |
| easy_002 | easy | 0.4000 |
| medium_001 | medium | 0.4000 |
| medium_002 | medium | 0.2500 |
| hard_001 | hard | 0.4000 |
| hard_002 | hard | 0.4000 |

| Level | Average |
|-------|---------|
| Easy | 0.4750 |
| Medium | 0.3250 |
| Hard | 0.4000 |
| **Overall** | **0.4000** |

The baseline is deterministic and uses no LLM.
An LLM-based agent using inference.py is expected to score higher.