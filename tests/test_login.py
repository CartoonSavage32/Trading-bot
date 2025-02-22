import pytest
from app.services.auth_manager import FyersAuthManager

@pytest.fixture
def auth_manager():
    return FyersAuthManager()

def test_login(auth_manager):
    success, auth_code = auth_manager.login()
    assert success is True
    assert isinstance(auth_code, str)