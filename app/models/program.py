import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Boolean, Text, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    program_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    giving_range_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    giving_range_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    success_definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_data_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_portfolio_based: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="programs")
