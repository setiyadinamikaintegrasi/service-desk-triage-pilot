from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Float, String, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from service_desk_triage.models import TicketPriority, TicketStatus


class Base(DeclarativeBase):
    pass


class TicketRecord(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reporter: Mapped[str] = mapped_column(String(320), nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=TicketStatus.OPEN,
    )
    priority: Mapped[TicketPriority | None] = mapped_column(
        Enum(
            TicketPriority,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=True,
    )
    triage_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    triage_summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    triage_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    triage_reasoning_code: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


def create_engine_and_session(
    database_url: str,
) -> tuple[Engine, sessionmaker[Session]]:
    engine = create_engine(database_url, future=True)
    return engine, sessionmaker(engine, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
