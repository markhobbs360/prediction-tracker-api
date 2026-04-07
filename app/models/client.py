import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    institution_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    crm_platform: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_import_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    platform_capabilities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    client_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    historical_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    box_folder_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    flowers_tenant_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    programs = relationship("Program", back_populates="client", lazy="selectin")
    features = relationship("Feature", back_populates="client", lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by], lazy="selectin")
