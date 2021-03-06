# -*- coding: utf-8 -*-
"""
Utilities for handling unicode and other repetitive bits
"""


def u(text, encoding="utf-8"):
    "Return unicode text, no matter what"

    if isinstance(text, bytes):
        text = text.decode(encoding)

    # it's already unicode
    text = text.replace("\r\n", "\n")
    return text
