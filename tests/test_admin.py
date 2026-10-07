import pytest
import requests

from config import BASE_URL, TIMEOUT
from api_helpers import auth_headers


@pytest.fixture
def api_session():
    with requests.Session() as session:
        session.headers.update({"Accept": "application/json"})
        yield session


def test_health_with_fixture(api_session):
    """GET /health,断言 200 与 {"status": "ok"}。用注入的 api_session 发请求。"""
    response = api_session.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    
@pytest.mark.parametrize(
    "token,expected_status,expected_value",
    [
        (None, 401, "missing_token"),
        ("wrong-token", 401, "invalid_token"),
        ("user-token", 403, "permission_denied"),
        ("admin-token", 200, "welcome_admin"),
    ],
    ids=["missing", "wrong", "user", "admin"],
)
def test_admin_permission(api_session, token, expected_status, expected_value):
    response = api_session.get(
        f"{BASE_URL}/admin", headers=auth_headers(token), timeout=TIMEOUT
    )
    assert response.status_code == expected_status,f"响应状态码不符合预期，响应内容：{response.text}"
    body = response.json()
    key = "message" if expected_status == 200 else "error"
    assert body[key] == expected_value
    print(auth_headers("admin-token"))