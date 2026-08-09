from service_desk_triage.models import TicketPriority
from service_desk_triage.triage import DeterministicTriageAdapter, TriageInput


def test_deterministic_triage_detects_security_critical_incident() -> None:
    adapter = DeterministicTriageAdapter()

    result = adapter.triage(
        TriageInput(
            title="Possible account breach",
            description=(
                "Multiple users report suspicious login activity and MFA prompts."
            ),
            reporter="security@example.com",
        )
    )

    assert result.category == "security"
    assert result.priority is TicketPriority.CRITICAL
    assert result.reasoning_code == "security_account_compromise"
    assert 0.0 <= result.confidence <= 1.0
    assert "suspicious login" in result.summary.lower()


def test_deterministic_triage_uses_low_priority_for_how_to_requests() -> None:
    adapter = DeterministicTriageAdapter()

    result = adapter.triage(
        TriageInput(
            title="How do I change my email signature?",
            description="Need instructions for updating my signature in email.",
            reporter="lee@example.com",
        )
    )

    assert result.category == "software"
    assert result.priority is TicketPriority.LOW
    assert result.reasoning_code == "software_how_to"
