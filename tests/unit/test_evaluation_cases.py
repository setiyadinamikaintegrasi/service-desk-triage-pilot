import json
from pathlib import Path

from service_desk_triage.triage import DeterministicTriageAdapter, TriageInput

GOLDEN_PATH = Path("evals/golden/service-desk-triage-golden.jsonl")


def test_service_desk_triage_golden_dataset_has_at_least_five_cases() -> None:
    cases = [json.loads(line) for line in GOLDEN_PATH.read_text().splitlines()]

    assert len(cases) >= 5
    assert all({"id", "input", "expected_output"} <= case.keys() for case in cases)


def test_deterministic_triage_matches_golden_cases() -> None:
    adapter = DeterministicTriageAdapter()
    cases = [json.loads(line) for line in GOLDEN_PATH.read_text().splitlines()]

    for case in cases:
        result = adapter.triage(TriageInput(**case["input"]))

        assert result.category == case["expected_output"]["category"], case["id"]
        assert result.priority.value == case["expected_output"]["priority"], case["id"]
        assert result.reasoning_code == case["expected_output"]["reasoning_code"], case[
            "id"
        ]
        assert result.confidence >= case["expected_output"]["minimum_confidence"], case[
            "id"
        ]
