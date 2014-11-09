# -*- coding: utf-8 -*-
"""
Utilities for handling unicode and other repetitive bits
"""
import six

def u(text, encoding='utf-8'):
    "Return unicode text, no matter what"

    if isinstance(text, six.binary_type):
        return text.decode(encoding)

    return six.text_type(text)