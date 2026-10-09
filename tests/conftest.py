import pytest
import requests
from config import BASE_URL, TIMEOUT


@pytest.fixture
def api_session():
    with requests.Session() as session:
        session.headers.update({"Accept": "application/json"})
        yield session


@pytest.fixture
def user_token(api_session):               
    response = api_session.post(
        f"{BASE_URL}/login",
        json={"username": "qa01", "password": "123456"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, f"前置登录失败：{response.text}"
    return response.json()["token"]