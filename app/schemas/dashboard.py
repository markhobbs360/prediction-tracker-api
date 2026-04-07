from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_clients: int
    active_intakes: int
    predictions_in_progress: int
    analyses_delivered: int
    pending_feedback: int


class PipelineItem(BaseModel):
    id: UUID
    title: str
    client_name: str
    stage: str
    status: str
    updated_at: datetime


class CrossClientInsightOut(BaseModel):
    id: UUID
    insight_type: str
    title: str
    description: str | None = None
    supporting_data: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
