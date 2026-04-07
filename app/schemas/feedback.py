from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    usage_type: str | None = None
    outcome_data: dict | None = None
    ask_amount_feedback: dict | None = None
    behavioral_data_notes: str | None = None
    client_feedback: str | None = None
    lessons_learned: str | None = None


class FeedbackUpdate(BaseModel):
    usage_type: str | None = None
    outcome_data: dict | None = None
    ask_amount_feedback: dict | None = None
    behavioral_data_notes: str | None = None
    client_feedback: str | None = None
    lessons_learned: str | None = None


class FeedbackOut(BaseModel):
    id: UUID
    analysis_id: UUID
    client_id: UUID
    usage_type: str | None = None
    outcome_data: dict | None = None
    ask_amount_feedback: dict | None = None
    behavioral_data_notes: str | None = None
    client_feedback: str | None = None
    lessons_learned: str | None = None
    recorded_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
