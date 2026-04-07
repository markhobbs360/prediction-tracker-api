import uuid
from datetime import datetime

from sqlalchemy import String, Text, JSON, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intake_brief_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("intake_briefs.id"), index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    flowers_prediction_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    intake_brief = relationship("IntakeBrief", lazy="selectin")
    client = relationship("Client", lazy="selectin")
    versions = relationship("PredictionVersion", back_populates="prediction", lazy="selectin", order_by="PredictionVersion.version_number")
    creator = relationship("User", foreign_keys=[created_by], lazy="selectin")


class PredictionVersion(Base):
    __tablename__ = "prediction_versions"
    __table_args__ = (
        UniqueConstraint("prediction_id", "version_number", name="uq_prediction_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prediction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("predictions.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    methodology_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_changes: Mapped[str | None] = mapped_column(Text, nullable=True)
    list_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    prediction = relationship("Prediction", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by], lazy="selectin")
