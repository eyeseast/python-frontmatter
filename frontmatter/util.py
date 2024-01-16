# -*- coding: utf-8 -*-
"""
Utilities for handling unicode and other repetitive bits
"""
from typing import AnyStr


def u(text: AnyStr, encoding: str = "utf-8") -> str:
    "Return unicode text, no matter what"

    if isinstance(text, bytes):
        text_str: str = text.decode(encoding)
    else:
        text_str = text

    # it's already unicode
    text_str = text_str.replace("\r\n", "\n")
    return text_str
