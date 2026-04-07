from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class AnalysisCreate(BaseModel):
    title: str
    overview_data: dict | None = None
    model_features_data: dict | None = None
    audit_detail_data: dict | None = None
    designations_data: dict | None = None
    recommendations: str | None = None
    quality_score: int | None = None
    quality_detail: dict | None = None
    box_report_url: str | None = None


class AnalysisUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    overview_data: dict | None = None
    model_features_data: dict | None = None
    audit_detail_data: dict | None = None
    designations_data: dict | None = None
    recommendations: str | None = None
    quality_score: int | None = None
    quality_detail: dict | None = None
    box_report_url: str | None = None


class AnalysisOut(BaseModel):
    id: UUID
    prediction_id: UUID
    client_id: UUID
    title: str
    status: str
    overview_data: dict | None = None
    model_features_data: dict | None = None
    audit_detail_data: dict | None = None
    designations_data: dict | None = None
    recommendations: str | None = None
    quality_score: int | None = None
    quality_detail: dict | None = None
    box_report_url: str | None = None
    delivered_at: datetime | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
