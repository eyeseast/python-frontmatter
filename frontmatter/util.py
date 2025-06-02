# -*- coding: utf-8 -*-
"""
Utilities for handling unicode and other repetitive bits
"""
from os import PathLike
from typing import TypeGuard, TextIO


def is_readable(fd: object) -> TypeGuard[TextIO]:
    return callable(getattr(fd, "read", None))


def is_writable(fd: object) -> TypeGuard[TextIO]:
    return callable(getattr(fd, "write", None))


def can_open(fd: object) -> TypeGuard[str | PathLike[str]]:
    return isinstance(fd, str) or isinstance(fd, PathLike)


def u(text: str | bytes, encoding: str = "utf-8") -> str:
    "Return unicode text, no matter what"

    if isinstance(text, bytes):
        text_str: str = text.decode(encoding)
    else:
        text_str = str(text)

    # it's already unicode
    text_str = text_str.replace("\r\n", "\n")
    return text_str
