from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field, field_validator

from service_desk_triage.models import TicketPriority, TriageResult


class TriageInput(BaseModel):
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


class TriageAdapter(Protocol):
    def triage(self, item: TriageInput) -> TriageResult: ...


class DeterministicTriageAdapter:
    def triage(self, item: TriageInput) -> TriageResult:
        text = f"{item.title} {item.description}".lower()
        summary = _summary(item.description)

        if _contains_any(text, ("phishing", "breach", "suspicious login", "mfa")):
            return TriageResult(
                category="security",
                priority=TicketPriority.CRITICAL,
                summary=summary,
                confidence=0.95,
                reasoning_code="security_account_compromise",
            )
        if _contains_any(text, ("vpn", "outage", "cannot connect", "down")):
            return TriageResult(
                category="network",
                priority=TicketPriority.HIGH,
                summary=summary,
                confidence=0.9,
                reasoning_code="network_connectivity_outage",
            )
        if _contains_any(text, ("will not boot", "screen stays black", "laptop")):
            return TriageResult(
                category="hardware",
                priority=TicketPriority.MEDIUM,
                summary=summary,
                confidence=0.85,
                reasoning_code="hardware_device_failure",
            )
        if _contains_any(text, ("how do i", "instructions", "signature")):
            return TriageResult(
                category="software",
                priority=TicketPriority.LOW,
                summary=summary,
                confidence=0.8,
                reasoning_code="software_how_to",
            )
        if _contains_any(text, ("sso", "password reset", "cannot access", "login")):
            return TriageResult(
                category="access",
                priority=TicketPriority.MEDIUM,
                summary=summary,
                confidence=0.85,
                reasoning_code="access_authentication_failure",
            )
        return TriageResult(
            category="software",
            priority=TicketPriority.LOW,
            summary=summary,
            confidence=0.7,
            reasoning_code="software_general_request",
        )


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _summary(description: str) -> str:
    return description.strip()[:500]
