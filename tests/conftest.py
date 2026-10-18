import subprocess
import sys
import time
import logging
from pathlib import Path

import pytest
import requests

from config import BASE_URL, TIMEOUT

logger = logging.getLogger("api")
LOCAL_URL = "http://127.0.0.1:8000"
SERVER_SCRIPT = Path(__file__).parent.parent / "server" / "local_api.py"


def _is_up(url):
    """服务能访问就返回 True,连不上就返回 False。"""
    try:
        with requests.Session() as session:
            session.trust_env = False
            session.get(f"{url}/health", timeout=0.5)
        return True
    except requests.ConnectionError:
        return False


def _log_response(response, **kwargs):
    """每收到一个响应，就记一条日志。"""
    request = response.request
    logger.info(
        "%s %s -> %s (%.0f ms)",
        request.method,
        request.url,
        response.status_code,
        response.elapsed.total_seconds() * 1000,
    )
    logger.info("  请求体：%s", request.body)
    logger.info("  响应体：%s", response.text.strip())


@pytest.fixture(scope="session", autouse=True)
def local_server():
    """测本地服务时自动启动它，全部测试结束后关掉。"""
    if BASE_URL != LOCAL_URL or _is_up(LOCAL_URL):
        yield
        return

    process = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 5
    while not _is_up(LOCAL_URL):
        if time.time() > deadline:
            process.terminate()
            pytest.fail("本地服务 5 秒内没有启动")
        time.sleep(0.1)

    yield

    process.terminate()
    process.wait()                          


@pytest.fixture
def api_session():
    with requests.Session() as session:
        session.trust_env = False #绕代理
        session.headers.update({"Accept": "application/json"})
        session.hooks["response"].append(_log_response)
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