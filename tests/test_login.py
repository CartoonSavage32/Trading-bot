import pytest
from app.services.auth_manager import FyersAuthManager


@pytest.fixture
def auth_manager():
    return FyersAuthManager()


def test_login(auth_manager):
    profile = auth_manager.login()
    assert profile["s"] == "ok"
    assert profile["code"] == 200
    assert isinstance(profile["data"], dict)
