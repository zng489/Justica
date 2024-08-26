import pytest

from authentication.utils import get_codigo_tribunal


def test_get_codigo_tribunal():
    decoded_token = {"corporativo": [{"seq_tribunal_pai": "42"}]}

    assert get_codigo_tribunal(decoded_token) == "42"


def test_get_codigo_tribunal_silent():
    decoded_token = {"corporativo": []}

    assert get_codigo_tribunal(decoded_token, silent=True) is None


def test_get_codigo_tribunal_decoded_token_is_none():
    decoded_token = None

    assert get_codigo_tribunal(decoded_token, silent=True) is None


def test_get_codigo_tribunal_do_not_raise_error():
    decoded_token = {"corporativo": []}

    assert get_codigo_tribunal(decoded_token, silent=True) is None


def test_get_codigo_tribunal_raise_error():
    decoded_token = {"corporativo": []}

    with pytest.raises(ValueError):
        get_codigo_tribunal(decoded_token, silent=False)
