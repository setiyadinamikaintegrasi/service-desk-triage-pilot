from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from service_desk_triage.database import TicketRecord
from service_desk_triage.models import (
    Ticket,
    TicketCreate,
    TicketPriority,
    TicketStatus,
    TriageResult,
    ticket_from_record,
    validate_status_transition,
)


class TicketRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_ticket(self, ticket: TicketCreate) -> Ticket:
        record = TicketRecord(
            id=str(uuid4()),
            title=ticket.title,
            description=ticket.description,
            reporter=ticket.reporter,
            status=TicketStatus.OPEN,
        )
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return ticket_from_record(record)

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        record = self._session.get(TicketRecord, ticket_id)
        if record is None:
            return None
        return ticket_from_record(record)

    def list_tickets(
        self,
        *,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
    ) -> list[Ticket]:
        statement: Select[tuple[TicketRecord]] = select(TicketRecord)
        if status is not None:
            statement = statement.where(TicketRecord.status == status)
        if priority is not None:
            statement = statement.where(TicketRecord.priority == priority)
        statement = statement.order_by(TicketRecord.created_at, TicketRecord.id)
        return [
            ticket_from_record(record)
            for record in self._session.scalars(statement).all()
        ]

    def apply_triage(self, ticket_id: str, result: TriageResult) -> Ticket | None:
        record = self._session.get(TicketRecord, ticket_id)
        if record is None:
            return None

        record.status = validate_status_transition(
            record.status,
            TicketStatus.IN_PROGRESS,
        )
        record.priority = result.priority
        record.triage_category = result.category
        record.triage_summary = result.summary
        record.triage_confidence = result.confidence
        record.triage_reasoning_code = result.reasoning_code
        self._session.commit()
        self._session.refresh(record)
        return ticket_from_record(record)
