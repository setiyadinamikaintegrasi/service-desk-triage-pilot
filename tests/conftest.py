from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from service_desk_triage.main import create_app


@pytest.fixture
def sqlite_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'tickets.db'}"


@pytest.fixture
def client(sqlite_url: str) -> Iterator[TestClient]:
    app = create_app(database_url=sqlite_url)
    with TestClient(app) as test_client:
        yield test_client
