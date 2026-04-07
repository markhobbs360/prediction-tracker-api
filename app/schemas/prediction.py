from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from app.schemas.intake import IntakeOut


class PredictionVersionCreate(BaseModel):
    parameters: dict | None = None
    methodology_notes: str | None = None
    criteria_changes: str | None = None
    list_size: int | None = None
    result_summary: dict | None = None


class PredictionVersionOut(BaseModel):
    id: UUID
    prediction_id: UUID
    version_number: int
    parameters: dict | None = None
    methodology_notes: str | None = None
    criteria_changes: str | None = None
    list_size: int | None = None
    result_summary: dict | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class PredictionCreate(BaseModel):
    flowers_prediction_url: str | None = None
    notes: str | None = None
    version: PredictionVersionCreate | None = None


class PredictionUpdate(BaseModel):
    flowers_prediction_url: str | None = None
    notes: str | None = None
    status: str | None = None


class PredictionOut(BaseModel):
    id: UUID
    intake_brief_id: UUID
    client_id: UUID
    status: str
    flowers_prediction_url: str | None = None
    current_version: int
    notes: str | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    versions: list[PredictionVersionOut] = []
    intake_brief: IntakeOut | None = None

    model_config = {"from_attributes": True}
