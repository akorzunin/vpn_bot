"""Check connection via pipvpn"""

import pytest

from src.fastapi_app import pivpn_wrapper

from tests import mock_globals

pivpn_wrapper.PIVPN_HOST = mock_globals.PIVPN_HOST


def test_check_pivpn_connection():
    """Test check_pivpn_connection"""
    assert pivpn_wrapper.check_pivpn_connection()
