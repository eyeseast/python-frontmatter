"""Tests for frontmatter.util: unicode normalisation and fd classification."""

import pathlib
from io import StringIO

import pytest

from frontmatter.util import can_open, is_readable, is_writable, u


@pytest.mark.parametrize(
    "value,expected",
    [
        (b"hello", "hello"),
        ("hello", "hello"),
        (b"a\r\nb", "a\nb"),  # CRLF normalised for bytes
        ("a\r\nb\r\nc", "a\nb\nc"),  # ... and for str
        ("a\nb", "a\nb"),  # LF untouched
        (123, "123"),  # non-str input is stringified
        (None, "None"),  # quirk: str(None)
        ("", ""),
        (b"", ""),
    ],
)
def test_u(value, expected):
    assert u(value) == expected


def test_u_custom_encoding():
    assert u("héllo".encode("latin-1"), encoding="latin-1") == "héllo"


def test_is_readable():
    assert is_readable(StringIO("x")) is True
    assert is_readable("a/path") is False
    assert is_readable(123) is False
    assert is_readable(None) is False
    assert is_readable(object()) is False


def test_is_writable():
    assert is_writable(StringIO()) is True
    assert is_writable("a/path") is False
    assert is_writable(123) is False


def test_can_open():
    assert can_open("a/path") is True
    assert can_open(pathlib.Path("a/path")) is True
    assert can_open(123) is False
    assert can_open(StringIO("x")) is False
    assert can_open(None) is False
