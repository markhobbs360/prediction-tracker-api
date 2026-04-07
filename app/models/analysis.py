import uuid
from datetime import datetime

from sqlalchemy import String, Text, JSON, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prediction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("predictions.id"), index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    overview_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    model_features_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    audit_detail_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    designations_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quality_detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    box_report_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    prediction = relationship("Prediction", lazy="selectin")
    client = relationship("Client", lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by], lazy="selectin")
