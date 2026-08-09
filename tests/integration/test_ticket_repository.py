from service_desk_triage.database import create_engine_and_session, init_db
from service_desk_triage.models import TicketCreate, TicketPriority, TicketStatus
from service_desk_triage.repository import TicketRepository
from service_desk_triage.triage import DeterministicTriageAdapter, TriageInput


def test_ticket_persists_across_sqlite_sessions(sqlite_url: str) -> None:
    engine, session_factory = create_engine_and_session(sqlite_url)
    init_db(engine)
    with session_factory() as session:
        created = TicketRepository(session).create_ticket(
            TicketCreate(
                title="Laptop will not boot",
                description="Power button lights up but screen stays black.",
                reporter="mira@example.com",
            )
        )

    with session_factory() as session:
        loaded = TicketRepository(session).get_ticket(created.id)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.title == "Laptop will not boot"
    assert loaded.status is TicketStatus.OPEN


def test_repository_filters_by_status_and_priority(sqlite_url: str) -> None:
    engine, session_factory = create_engine_and_session(sqlite_url)
    init_db(engine)
    with session_factory() as session:
        repo = TicketRepository(session)
        vpn = repo.create_ticket(
            TicketCreate(
                title="VPN down",
                description="The whole team cannot connect to VPN.",
                reporter="ops@example.com",
            )
        )
        mouse = repo.create_ticket(
            TicketCreate(
                title="Mouse replacement",
                description="Bluetooth mouse battery cover is missing.",
                reporter="sam@example.com",
            )
        )
        repo.apply_triage(
            vpn.id,
            DeterministicTriageAdapter().triage(
                TriageInput(
                    title=vpn.title,
                    description=vpn.description,
                    reporter=vpn.reporter,
                )
            ),
        )
        repo.apply_triage(
            mouse.id,
            DeterministicTriageAdapter().triage(
                TriageInput(
                    title=mouse.title,
                    description=mouse.description,
                    reporter=mouse.reporter,
                )
            ),
        )

        high_priority = repo.list_tickets(priority=TicketPriority.HIGH)
        in_progress = repo.list_tickets(status=TicketStatus.IN_PROGRESS)

    assert [ticket.id for ticket in high_priority] == [vpn.id]
    assert {ticket.id for ticket in in_progress} == {vpn.id, mouse.id}
