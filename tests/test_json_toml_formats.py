"""Tests for the JSON and TOML handlers: parsing, export quirks, round trips."""

import datetime

import pytest

import frontmatter
from frontmatter.default_handlers import JSONHandler, TOMLHandler

toml = pytest.importorskip("toml")

JSON_DOC = '{\n"title": "JSON Post",\n"count": 3,\n"tags": ["a", "b"]\n}\nBody here'

TOML_DOC = (
    '+++\ntitle = "TOML Post"\ncount = 7\npi = 3.14\ndraft = false\n'
    "when = 2024-01-15T10:30:00Z\n"
    'tags = ["x", "y"]\n[author]\nname = "bob"\n+++\nTOML body'
)


# ---------------- JSON ----------------


def test_json_post_parses_with_json_handler():
    post = frontmatter.loads(JSON_DOC)
    assert isinstance(post.handler, JSONHandler)
    assert post.metadata == {"title": "JSON Post", "count": 3, "tags": ["a", "b"]}
    assert post.content == "Body here"


def test_json_round_trip():
    post = frontmatter.loads(JSON_DOC)
    repost = frontmatter.loads(frontmatter.dumps(post))
    assert repost.metadata == post.metadata
    assert repost.content == post.content


def test_json_dumps_exact_output():
    # The JSON handler's delimiters are empty strings, so the shared
    # post template leaves an extra blank line before the content.
    post = frontmatter.loads(JSON_DOC)
    assert frontmatter.dumps(post) == (
        '{\n    "title": "JSON Post",\n    "count": 3,\n    "tags": [\n'
        '        "a",\n        "b"\n    ]\n}\n\n\nBody here'
    )


def test_json_export_indents_and_preserves_key_order():
    assert JSONHandler().export({"b": 1, "a": [1, 2]}) == (
        '{\n    "b": 1,\n    "a": [\n        1,\n        2\n    ]\n}'
    )


def test_json_braces_inside_content_survive():
    post = frontmatter.loads('{\n"a": 1\n}\nbody with } brace\nand { brace')
    assert post.metadata == {"a": 1}
    assert post.content == "body with } brace\nand { brace"


def test_json_invalid_frontmatter_raises():
    with pytest.raises(Exception, match="Expecting value"):
        frontmatter.loads('{\n"a": broken\n}\nbody')


def test_dumps_empty_post_as_json():
    post = frontmatter.Post("body")
    assert frontmatter.dumps(post, handler=JSONHandler()) == "{}\n\n\nbody"


# ---------------- TOML ----------------


def test_toml_post_parses_with_toml_handler():
    post = frontmatter.loads(TOML_DOC)
    assert isinstance(post.handler, TOMLHandler)
    assert post["title"] == "TOML Post"
    assert post["count"] == 7
    assert post["pi"] == 3.14
    assert post["draft"] is False
    assert post["tags"] == ["x", "y"]
    assert post["author"] == {"name": "bob"}
    assert post.content == "TOML body"


def test_toml_datetime_value():
    post = frontmatter.loads(TOML_DOC)
    when = post["when"]
    assert isinstance(when, datetime.datetime)
    assert (when.year, when.month, when.day, when.hour, when.minute) == (
        2024,
        1,
        15,
        10,
        30,
    )


def test_toml_round_trip():
    post = frontmatter.loads(TOML_DOC)
    repost = frontmatter.loads(frontmatter.dumps(post))
    assert repost.metadata == post.metadata
    assert repost.content == post.content


def test_toml_export_nested_table():
    assert TOMLHandler().export({"a": 1, "b": {"c": 2}}) == "a = 1\n\n[b]\nc = 2\n"


def test_toml_invalid_frontmatter_raises():
    with pytest.raises(toml.TomlDecodeError):
        frontmatter.loads("+++\na = =\n+++\nbody")


def test_dumps_empty_post_as_toml():
    post = frontmatter.Post("body")
    assert frontmatter.dumps(post, handler=TOMLHandler()) == "+++\n\n+++\n\nbody"


def test_dumps_with_handler_override_changes_format():
    post = frontmatter.loads("---\na: 1\n---\nx")
    assert frontmatter.dumps(post, handler=TOMLHandler()) == "+++\na = 1\n\n+++\n\nx"
