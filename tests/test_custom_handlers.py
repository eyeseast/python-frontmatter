"""Tests for BaseHandler and for registering custom handlers.

Custom-format support is a headline feature of the library but is only
exercised in the existing tests by a duck-typed dummy; here a real
BaseHandler subclass is driven end to end.
"""

import re

import pytest

import frontmatter
from frontmatter.default_handlers import BaseHandler


class SemiHandler(BaseHandler):
    """A ``key = value`` format delimited by ;;; lines."""

    FM_BOUNDARY = re.compile(r"^;;;\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = ";;;"

    def load(self, fm):
        out = {}
        for line in fm.strip().splitlines():
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip()
        return out

    def export(self, metadata, **kwargs):
        return "\n".join(f"{k} = {v}" for k, v in metadata.items())


def test_base_handler_without_boundary_raises_not_implemented():
    class NoBoundary(BaseHandler):
        pass

    with pytest.raises(NotImplementedError, match="No frontmatter boundary defined"):
        NoBoundary()


def test_base_handler_load_and_export_are_abstract():
    handler = BaseHandler(fm_boundary=re.compile("x"))
    with pytest.raises(NotImplementedError):
        handler.load("x")
    with pytest.raises(NotImplementedError):
        handler.export({})


def test_base_handler_detect_uses_boundary():
    handler = SemiHandler()
    assert handler.detect(";;;\na = b\n;;;\nx") is True
    assert handler.detect("---\na: 1\n---\nx") is False


def test_split_value_error_bails_out_of_parse():
    class BadSplit(SemiHandler):
        def split(self, text):
            raise ValueError("boom")

    # parse() catches the ValueError from split and returns the
    # defaults plus the untouched text.
    assert frontmatter.parse(";;;\na = b\n;;;\nbody", handler=BadSplit()) == (
        {},
        ";;;\na = b\n;;;\nbody",
    )


def test_custom_handler_end_to_end():
    post = frontmatter.loads(";;;\ntitle = Semi\n;;;\nbody", handler=SemiHandler())
    assert post.metadata == {"title": "Semi"}
    assert post.content == "body"
    assert frontmatter.dumps(post) == ";;;\ntitle = Semi\n;;;\n\nbody"


def test_custom_handler_registered_in_global_handlers():
    frontmatter.handlers.append(SemiHandler())
    try:
        detected = frontmatter.detect_format(";;;\na = b\n;;;\nx", frontmatter.handlers)
        assert isinstance(detected, SemiHandler)
        assert frontmatter.loads(";;;\na = b\n;;;\nx").metadata == {"a": "b"}
    finally:
        frontmatter.handlers.pop()


def test_builtin_handlers_win_over_later_registrations():
    # Detection walks the handlers list in order; YAML is first.
    frontmatter.handlers.append(SemiHandler())
    try:
        detected = frontmatter.detect_format("---\na: 1\n---\nx", frontmatter.handlers)
        assert type(detected).__name__ == "YAMLHandler"
    finally:
        frontmatter.handlers.pop()
