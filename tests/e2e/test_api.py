from fastapi.testclient import TestClient


def test_health_returns_status_and_version(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_create_get_and_list_ticket(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Cannot access payroll",
            "description": "Payroll app rejects my SSO login after password reset.",
            "reporter": "rani@example.com",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"]
    assert created["status"] == "open"
    assert created["priority"] is None
    assert created["created_at"].endswith("Z")

    get_response = client.get(f"/api/v1/tickets/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Cannot access payroll"

    list_response = client.get("/api/v1/tickets", params={"status": "open"})
    assert list_response.status_code == 200
    assert [ticket["id"] for ticket in list_response.json()["items"]] == [created["id"]]


def test_list_filters_by_status_and_priority_after_triage(client: TestClient) -> None:
    first = client.post(
        "/api/v1/tickets",
        json={
            "title": "VPN outage",
            "description": "Entire finance team cannot connect to the VPN.",
            "reporter": "finance@example.com",
        },
    ).json()
    client.post(
        "/api/v1/tickets",
        json={
            "title": "Keyboard request",
            "description": "Need a replacement keyboard for a new desk setup.",
            "reporter": "people@example.com",
        },
    )

    triage_response = client.post(f"/api/v1/tickets/{first['id']}/triage")

    assert triage_response.status_code == 200
    assert triage_response.json()["priority"] == "high"
    filtered = client.get(
        "/api/v1/tickets",
        params={"status": "in_progress", "priority": "high"},
    )
    assert [ticket["id"] for ticket in filtered.json()["items"]] == [first["id"]]


def test_create_ticket_rejects_invalid_input(client: TestClient) -> None:
    response = client.post(
        "/api/v1/tickets",
        json={"title": "", "description": "short", "reporter": ""},
    )

    assert response.status_code == 422
    locations = {tuple(error["loc"]) for error in response.json()["detail"]}
    assert ("body", "title") in locations
    assert ("body", "reporter") in locations


def test_get_missing_ticket_returns_consistent_404(client: TestClient) -> None:
    response = client.get("/api/v1/tickets/ticket-does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "not_found",
            "message": "Ticket not found",
        }
    }


def test_triage_missing_ticket_returns_consistent_404(client: TestClient) -> None:
    response = client.post("/api/v1/tickets/ticket-does-not-exist/triage")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "not_found",
            "message": "Ticket not found",
        }
    }


def test_triage_ticket_returns_validated_result_and_updates_ticket(
    client: TestClient,
) -> None:
    created = client.post(
        "/api/v1/tickets",
        json={
            "title": "Suspected phishing email",
            "description": (
                "User clicked a phishing link and reports suspicious MFA prompts."
            ),
            "reporter": "it@example.com",
        },
    ).json()

    response = client.post(f"/api/v1/tickets/{created['id']}/triage")

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "security"
    assert body["priority"] == "critical"
    assert body["reasoning_code"] == "security_account_compromise"
    assert 0 <= body["confidence"] <= 1

    get_response = client.get(f"/api/v1/tickets/{created['id']}")
    ticket = get_response.json()
    assert ticket["status"] == "in_progress"
    assert ticket["priority"] == "critical"
    assert ticket["triage"]["category"] == "security"
