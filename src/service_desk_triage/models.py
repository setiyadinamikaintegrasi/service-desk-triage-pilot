from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class TicketPriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TicketCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str = Field(max_length=4000)
    reporter: str = Field(max_length=320)

    @field_validator("title", "description", "reporter")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field must not be blank")
        return stripped


class TriageResult(BaseModel):
    category: str = Field(max_length=80)
    priority: TicketPriority
    summary: str = Field(max_length=500)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_code: str = Field(max_length=120)

    @field_validator("category", "summary", "reasoning_code")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field must not be blank")
        return stripped


class Ticket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    reporter: str
    status: TicketStatus
    priority: TicketPriority | None = None
    triage: TriageResult | None = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        normalized = (
            value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
        )
        return normalized.isoformat().replace("+00:00", "Z")


def validate_status_transition(
    current: TicketStatus,
    target: TicketStatus,
) -> TicketStatus:
    allowed: dict[TicketStatus, set[TicketStatus]] = {
        TicketStatus.OPEN: {TicketStatus.OPEN, TicketStatus.IN_PROGRESS},
        TicketStatus.IN_PROGRESS: {
            TicketStatus.IN_PROGRESS,
            TicketStatus.RESOLVED,
        },
        TicketStatus.RESOLVED: {TicketStatus.RESOLVED},
    }
    if target not in allowed[current]:
        raise ValueError(
            f"Cannot transition ticket from {current.value} to {target.value}"
        )
    return target


def triage_from_record(record: Any) -> TriageResult | None:
    if record.triage_category is None:
        return None
    return TriageResult(
        category=record.triage_category,
        priority=record.priority,
        summary=record.triage_summary,
        confidence=record.triage_confidence,
        reasoning_code=record.triage_reasoning_code,
    )


def ticket_from_record(record: Any) -> Ticket:
    return Ticket(
        id=record.id,
        title=record.title,
        description=record.description,
        reporter=record.reporter,
        status=record.status,
        priority=record.priority,
        triage=triage_from_record(record),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
