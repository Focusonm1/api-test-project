from config import BASE_URL, TIMEOUT


def test_health_with_fixture(api_session):
    response = api_session.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}