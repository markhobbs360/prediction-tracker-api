from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from app.schemas.client import ProgramOut


class IntakeCreate(BaseModel):
    client_id: UUID
    program_id: UUID
    title: str
    objective: str | None = None
    training_data_alignment: dict | None = None
    feature_checklist: dict | None = None
    segmentation_requirements: dict | None = None
    portfolio_fields: dict | None = None
    client_expectations: str | None = None
    jira_issue_key: str | None = None
    notes: str | None = None


class IntakeUpdate(BaseModel):
    title: str | None = None
    objective: str | None = None
    training_data_alignment: dict | None = None
    feature_checklist: dict | None = None
    segmentation_requirements: dict | None = None
    portfolio_fields: dict | None = None
    client_expectations: str | None = None
    override_justification: str | None = None
    jira_issue_key: str | None = None
    notes: str | None = None


class IntakeOut(BaseModel):
    id: UUID
    client_id: UUID
    program_id: UUID
    title: str
    objective: str | None = None
    training_data_alignment: dict | None = None
    feature_checklist: dict | None = None
    segmentation_requirements: dict | None = None
    portfolio_fields: dict | None = None
    data_readiness_score: int | None = None
    data_readiness_detail: dict | None = None
    client_expectations: str | None = None
    status: str
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    rejection_reason: str | None = None
    override_justification: str | None = None
    jira_issue_key: str | None = None
    notes: str | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    program: ProgramOut | None = None

    model_config = {"from_attributes": True}


class GateCheck(BaseModel):
    name: str
    passed: bool
    message: str


class GateResult(BaseModel):
    can_proceed: bool
    checks: list[GateCheck]


class DataReadinessResult(BaseModel):
    score: int
    detail: dict
