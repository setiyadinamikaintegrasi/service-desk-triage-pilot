import pytest
from pydantic import ValidationError

from service_desk_triage.models import (
    TicketCreate,
    TicketPriority,
    TicketStatus,
    TriageResult,
    validate_status_transition,
)


def test_ticket_create_rejects_blank_required_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TicketCreate(title=" ", description="Cannot connect", reporter="")

    errors = {tuple(error["loc"]) for error in exc_info.value.errors()}
    assert ("title",) in errors
    assert ("reporter",) in errors


def test_ticket_create_limits_description_length() -> None:
    with pytest.raises(ValidationError):
        TicketCreate(
            title="VPN problem",
            description="x" * 4001,
            reporter="ana@example.com",
        )


def test_triage_result_rejects_invalid_structured_output() -> None:
    with pytest.raises(ValidationError):
        TriageResult(
            category="network",
            priority="urgent",
            summary="VPN cannot connect",
            confidence=1.7,
            reasoning_code="network_vpn",
        )


def test_status_transition_allows_open_to_in_progress() -> None:
    assert (
        validate_status_transition(TicketStatus.OPEN, TicketStatus.IN_PROGRESS)
        == TicketStatus.IN_PROGRESS
    )


def test_status_transition_rejects_resolved_to_in_progress() -> None:
    with pytest.raises(ValueError, match="Cannot transition"):
        validate_status_transition(TicketStatus.RESOLVED, TicketStatus.IN_PROGRESS)


def test_priority_enum_contains_requested_values_only() -> None:
    assert {priority.value for priority in TicketPriority} == {
        "critical",
        "high",
        "medium",
        "low",
    }
