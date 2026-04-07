import uuid
from datetime import datetime

from sqlalchemy import String, Text, JSON, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IntakeBrief(Base):
    __tablename__ = "intake_briefs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_data_alignment: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    feature_checklist: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    segmentation_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    portfolio_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    data_readiness_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_readiness_detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    client_expectations: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    jira_issue_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    client = relationship("Client", lazy="selectin")
    program = relationship("Program", lazy="selectin")
    approver = relationship("User", foreign_keys=[approved_by], lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by], lazy="selectin")
