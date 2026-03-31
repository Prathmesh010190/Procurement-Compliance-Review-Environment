def rule_based_decision(obs):
    amount = obs.get("amount_usd", 0)
    budget = obs.get("budget_remaining_usd", 0)
    vendor = obs.get("vendor_status", "")
    manager = obs.get("manager_approval", False)
    finance = obs.get("finance_approval", False)
    security = obs.get("security_review", False)
    item_type = obs.get("item_type", "").lower()

    route_to = []
    missing = []
    policy = "compliant"
    risk = "low"

    # Manager approval check
    if not manager:
        route_to.append("manager")
        missing.append("manager approval")
        policy = "non_compliant"

    # Finance approval check
    if amount > 5000 and not finance:
        route_to.append("finance")
        missing.append("finance approval")
        policy = "non_compliant"

    # Security review check
    needs_security = item_type in ["software", "cloud service", "saas", "cloud_service"]
    if needs_security and not security:
        route_to.append("security")
        missing.append("security review")
        if policy == "compliant":
            policy = "partial"

    # Vendor check
    if vendor in ["unapproved", "new", "unknown"]:
        route_to.append("procurement")
        missing.append("vendor onboarding")
        if policy == "compliant":
            policy = "partial"

    # Budget check
    if amount > budget:
        missing.append("budget exception approval")
        if policy == "compliant":
            policy = "partial"

    # Risk level
    if amount > 10000:
        risk = "high"
    elif amount > 5000:
        risk = "medium"

    # Approval decision
    if len(missing) == 0:
        decision = "approved"
    elif len(missing) <= 2:
        decision = "needs_review"
    else:
        decision = "denied"

    return {
        "policy_compliance": policy,
        "approval_decision": decision,
        "risk_level": risk,
        "route_to": route_to,
        "missing_requirements": missing,
    }