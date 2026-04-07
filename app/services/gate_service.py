from app.models.intake_brief import IntakeBrief
from app.models.analysis import Analysis
from app.schemas.intake import GateCheck, GateResult


def can_start_prediction(intake: IntakeBrief) -> GateResult:
    """Check whether an intake brief passes the gate to start a prediction."""
    checks: list[GateCheck] = []

    # Check 1: status must be approved
    checks.append(GateCheck(
        name="intake_approved",
        passed=intake.status == "approved",
        message="Intake brief must be approved" if intake.status != "approved"
        else "Intake brief is approved",
    ))

    # Check 2: data readiness score >= 60 or override justification present
    score = intake.data_readiness_score or 0
    has_override = bool(intake.override_justification)
    score_ok = score >= 60 or has_override
    if score >= 60:
        msg = f"Data readiness score is {score} (>= 60)"
    elif has_override:
        msg = f"Data readiness score is {score} but override justification provided"
    else:
        msg = f"Data readiness score is {score} (< 60) and no override justification"
    checks.append(GateCheck(name="data_readiness", passed=score_ok, message=msg))

    # Check 3: required fields
    has_title = bool(intake.title)
    has_objective = bool(intake.objective)
    required_ok = has_title and has_objective
    missing = []
    if not has_title:
        missing.append("title")
    if not has_objective:
        missing.append("objective")
    checks.append(GateCheck(
        name="required_fields",
        passed=required_ok,
        message="All required fields present" if required_ok
        else f"Missing required fields: {', '.join(missing)}",
    ))

    can_proceed = all(c.passed for c in checks)
    return GateResult(can_proceed=can_proceed, checks=checks)


def can_deliver_analysis(analysis: Analysis) -> GateResult:
    """Check whether an analysis passes the gate for delivery."""
    checks: list[GateCheck] = []

    # Check 1: quality score >= 70 or None (not yet scored is allowed)
    q = analysis.quality_score
    quality_ok = q is None or q >= 70
    if q is None:
        msg = "Quality score not yet assigned (allowed)"
    elif q >= 70:
        msg = f"Quality score is {q} (>= 70)"
    else:
        msg = f"Quality score is {q} (< 70)"
    checks.append(GateCheck(name="quality_score", passed=quality_ok, message=msg))

    # Check 2: required sections present
    has_overview = analysis.overview_data is not None
    has_recommendations = bool(analysis.recommendations)
    sections_ok = has_overview and has_recommendations
    missing = []
    if not has_overview:
        missing.append("overview_data")
    if not has_recommendations:
        missing.append("recommendations")
    checks.append(GateCheck(
        name="required_sections",
        passed=sections_ok,
        message="All required sections present" if sections_ok
        else f"Missing required sections: {', '.join(missing)}",
    ))

    # Check 3: status must be internal_review or client_ready
    valid_statuses = {"internal_review", "client_ready"}
    status_ok = analysis.status in valid_statuses
    checks.append(GateCheck(
        name="status",
        passed=status_ok,
        message=f"Status is '{analysis.status}'" + (
            "" if status_ok else f" (must be one of: {', '.join(valid_statuses)})"
        ),
    ))

    can_proceed = all(c.passed for c in checks)
    return GateResult(can_proceed=can_proceed, checks=checks)
