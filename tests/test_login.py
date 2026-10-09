import pytest

from config import BASE_URL, TIMEOUT


def test_login_success(api_session):
    response = api_session.post(
        f"{BASE_URL}/login",
        json={"username": "qa01", "password": "123456"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    assert response.json() == {"token": "user-token","user": "qa01"}

@pytest.mark.parametrize(
    "body, expected_status, expected_error",
    [
        ({"username": "qa01", "password": "wrong"}, 401, "invalid_credentials"),
        ({"username": "nobody", "password": "123456"}, 401, "invalid_credentials"),
        ({"username": "qa01"}, 401, "invalid_credentials"),
        ({}, 401, "invalid_credentials"),
        (["qa01", "123456"], 400, "expected_json_object")
        ],
    ids=["wrong_password", "unknown-user", "missing_password", "empty_body", "not_object"],
)
def test_login_rejected(body,expected_status, expected_error, api_session):
    response = api_session.post(
        f"{BASE_URL}/login",
        json=body,
        timeout=TIMEOUT,
    )
    assert response.status_code == expected_status
    assert response.json() == {"error": expected_error}


def test_login_invalid_json(api_session):
    response = api_session.post(
        f"{BASE_URL}/login",
        data="not json",
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 400
    assert response.json() == {"error": "invalid_json"}
