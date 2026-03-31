---
title: Procurement Compliance Review Environment
emoji: 📋
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Procurement Compliance Review OpenEnv

A real-world OpenEnv environment for evaluating AI agents on procurement compliance review and approval routing.

## Problem Overview

Organizations process internal purchase requests for software, hardware, consulting, cloud services, and office equipment. Before approval, procurement and finance teams must verify whether requests comply with internal policy.

This environment simulates that workflow. An agent receives a procurement request and must determine:

- Policy compliance status
- Approval decision
- Risk level
- Routing destination
- Missing approval or policy requirements

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