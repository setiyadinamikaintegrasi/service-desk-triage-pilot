from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from service_desk_triage import __version__
from service_desk_triage.database import create_engine_and_session, init_db
from service_desk_triage.models import (
    Ticket,
    TicketCreate,
    TicketPriority,
    TicketStatus,
    TriageResult,
)
from service_desk_triage.repository import TicketRepository
from service_desk_triage.triage import DeterministicTriageAdapter, TriageInput


class TicketListResponse(BaseModel):
    items: list[Ticket]


def create_app(database_url: str = "sqlite:///./service-desk-triage.db") -> FastAPI:
    engine, session_factory = create_engine_and_session(database_url)
    init_db(engine)

    app = FastAPI(title="Service Desk Triage Pilot", version=__version__)

    def get_session() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    SessionDependency = Annotated[Session, Depends(get_session)]
    StatusFilter = Annotated[TicketStatus | None, Query(alias="status")]

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.post(
        "/api/v1/tickets",
        response_model=Ticket,
        status_code=status.HTTP_201_CREATED,
    )
    def create_ticket(
        ticket: TicketCreate,
        session: SessionDependency,
    ) -> Ticket:
        return TicketRepository(session).create_ticket(ticket)

    @app.get("/api/v1/tickets/{ticket_id}", response_model=Ticket)
    def get_ticket(
        ticket_id: str,
        session: SessionDependency,
    ) -> Ticket:
        ticket = TicketRepository(session).get_ticket(ticket_id)
        if ticket is None:
            raise _ticket_not_found()
        return ticket

    @app.get("/api/v1/tickets", response_model=TicketListResponse)
    def list_tickets(
        session: SessionDependency,
        status_filter: StatusFilter = None,
        priority: TicketPriority | None = None,
    ) -> TicketListResponse:
        tickets = TicketRepository(session).list_tickets(
            status=status_filter,
            priority=priority,
        )
        return TicketListResponse(items=tickets)

    @app.post("/api/v1/tickets/{ticket_id}/triage", response_model=TriageResult)
    def triage_ticket(
        ticket_id: str,
        session: SessionDependency,
    ) -> TriageResult:
        repository = TicketRepository(session)
        ticket = repository.get_ticket(ticket_id)
        if ticket is None:
            raise _ticket_not_found()

        result = DeterministicTriageAdapter().triage(
            TriageInput(
                title=ticket.title,
                description=ticket.description,
                reporter=ticket.reporter,
            )
        )
        repository.apply_triage(ticket_id, result)
        return result

    return app


def _ticket_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "not_found", "message": "Ticket not found"},
    )
