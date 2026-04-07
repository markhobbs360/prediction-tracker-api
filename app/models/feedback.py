import uuid
from datetime import datetime

from sqlalchemy import String, Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FeedbackEntry(Base):
    __tablename__ = "feedback_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analyses.id"), index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    usage_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    outcome_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ask_amount_feedback: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    behavioral_data_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    analysis = relationship("Analysis", lazy="selectin")
    client = relationship("Client", lazy="selectin")
    recorder = relationship("User", foreign_keys=[recorded_by], lazy="selectin")
