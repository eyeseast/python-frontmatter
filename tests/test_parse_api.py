"""Tests for the top-level parse/check/load/dump API semantics.

These complement tests/unit_test.py, which covers the fixture files:
here the focus is on parse() return values, default merging, detection
outcomes, file-like objects and error paths.
"""

import json
import pathlib
from io import StringIO

import pytest
import yaml

import frontmatter
from frontmatter.default_handlers import TOMLHandler, YAMLHandler


def test_parse_returns_metadata_and_content_tuple():
    metadata, content = frontmatter.parse("---\ntitle: T\n---\nbody text")
    assert metadata == {"title": "T"}
    assert content == "body text"


def test_parse_defaults_are_used_and_overridden():
    metadata, _ = frontmatter.parse(
        "---\ntitle: T\n---\nbody", author="default-a", title="default-t"
    )
    assert metadata == {"author": "default-a", "title": "T"}


def test_parse_no_frontmatter_returns_defaults_and_full_text():
    metadata, content = frontmatter.parse("just text", author="x")
    assert metadata == {"author": "x"}
    assert content == "just text"


def test_parse_empty_text():
    assert frontmatter.parse("") == ({}, "")


def test_parse_non_dict_frontmatter_is_ignored():
    # YAML front matter that parses to a list or a scalar cannot be
    # merged into the metadata dict, so it is silently dropped.
    assert frontmatter.parse("---\n- a\n- b\n---\nbody") == ({}, "body")
    assert frontmatter.parse("---\njust a string\n---\nbody") == ({}, "body")


def test_parse_unclosed_frontmatter_is_not_frontmatter():
    text = "---\na: 1\nno closing"
    assert frontmatter.parse(text) == ({}, text)


def test_parse_frontmatter_must_start_the_text():
    text = "intro\n---\na: 1\n---\nx"
    assert frontmatter.parse(text) == ({}, text)


def test_checks_on_strings():
    assert frontmatter.checks("---\na: 1\n---\nbody") is True
    assert frontmatter.checks("+++\na = 1\n+++\nbody") is True
    assert frontmatter.checks('{\n"a": 1\n}\nbody') is True
    assert frontmatter.checks("hello") is False
    assert frontmatter.checks("") is False


def test_checks_single_line_json_is_not_detected():
    # Quirk: the JSON handler's boundary only matches a line that is
    # exactly "{" or "}", so a one-line JSON document is not front matter.
    assert frontmatter.checks('{"a": 1}\nbody') is False


def test_detect_format_none_and_order():
    assert frontmatter.detect_format("hello", frontmatter.handlers) is None
    handler = frontmatter.detect_format("---\na: 1\n---\nx", frontmatter.handlers)
    assert isinstance(handler, YAMLHandler)
    assert [type(h).__name__ for h in frontmatter.handlers] == [
        "YAMLHandler",
        "JSONHandler",
        "TOMLHandler",
    ]


def test_loads_accepts_bytes():
    post = frontmatter.loads(b"---\na: 1\n---\nbody")
    assert post.metadata == {"a": 1}
    assert post.content == "body"


def test_load_and_check_accept_file_like_objects():
    assert frontmatter.load(StringIO("---\na: 2\n---\nbody")).metadata == {"a": 2}
    assert frontmatter.check(StringIO("---\na: 2\n---\nbody")) is True
    assert frontmatter.check(StringIO("plain")) is False


def test_check_with_unopenable_type_is_false():
    assert frontmatter.check(123) is False
    assert frontmatter.check(None) is False


def test_load_with_unopenable_type_raises_value_error():
    with pytest.raises(ValueError, match="Cannot open filename using type"):
        frontmatter.load(123)


def test_dump_with_unopenable_type_raises_value_error():
    with pytest.raises(ValueError, match="Cannot open filename using type"):
        frontmatter.dump(frontmatter.Post("x"), 123)


def test_load_missing_file_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        frontmatter.load("tests/yaml/does-not-exist.txt")


def test_check_missing_file_raises_instead_of_returning_false():
    # Quirk: check() opens the path, so a missing file raises rather
    # than returning False.
    with pytest.raises(FileNotFoundError):
        frontmatter.check("tests/yaml/does-not-exist.txt")


def test_dump_to_stringio_and_path(tmp_path):
    post = frontmatter.Post("x", a=1)
    f = StringIO()
    frontmatter.dump(post, f)
    assert f.getvalue() == "---\na: 1\n---\n\nx"

    target = tmp_path / "out.md"
    frontmatter.dump(post, target)
    assert target.read_text(encoding="utf-8") == f.getvalue()
    frontmatter.dump(post, str(target))
    assert frontmatter.load(target).metadata == {"a": 1}


def test_explicit_handler_skips_detection():
    # Passing a TOML handler for YAML-delimited text: the TOML boundary
    # never matches, splitting fails, and the metadata stays empty.
    post = frontmatter.loads("---\na: 1\n---\nx", handler=TOMLHandler())
    assert post.metadata == {}


def test_invalid_frontmatter_raises_parser_errors():
    with pytest.raises(yaml.parser.ParserError):
        frontmatter.loads("---\n: [unclosed\n---\nbody")
    with pytest.raises(json.JSONDecodeError):
        frontmatter.loads('{\n"a": broken\n}\nbody')
