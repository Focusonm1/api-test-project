import pytest
import requests


@pytest.fixture
def api_session():
    with requests.Session() as session:
        session.headers.update({"Accept": "application/json"})
        yield session
