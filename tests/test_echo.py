import pytest

from config import BASE_URL, TIMEOUT


@pytest.mark.parametrize(
    "params,expected_args",
    [
        ({"name": "qa01"}, {"name": "qa01"}),
        ({"name": "qa01", "role": "tester"}, {"name": "qa01", "role": "tester"}),
        ({}, {}),
        ({"name": "张三"}, {"name": "张三"}),
        ({"name": ["a", "b"]}, {"name": ["a", "b"]}),
    ],
    ids=["single", "multiple", "no-params", "chinese", "repeated-key"],
)
def test_echo_returns_query_args(api_session, params, expected_args):
    response = api_session.get(f"{BASE_URL}/echo", params=params, timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json() == {"args": expected_args}


def test_echo_drops_empty_value(api_session):
    """发现：空值参数会被服务丢弃，而不是返回空字符串。记录为待确认行为。"""
    response = api_session.get(
        f"{BASE_URL}/echo", params={"name": "qa01", "role": ""}, timeout=TIMEOUT
    )
    assert response.status_code == 200
    assert response.json() == {"args": {"name": "qa01"}}


def test_unknown_path_returns_404(api_session):
    response = api_session.get(f"{BASE_URL}/nope", timeout=TIMEOUT)
    assert response.status_code == 404
    assert response.json() == {"error": "not_found", "path": "/nope"}