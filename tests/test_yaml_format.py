"""Tests for YAML front matter: type coercion, delimiters and export."""

import datetime

import pytest

import frontmatter
from frontmatter.default_handlers import YAMLHandler

RICH = """\
---
int: 42
float: 3.5
bool: true
date: 2024-01-15
nothing: null
lst: [1, two, 3.0]
nested:
  x: 1
  y: two
quoted: '42'
---
body"""


def test_yaml_scalar_types_are_coerced():
    post = frontmatter.loads(RICH)
    assert post["int"] == 42 and isinstance(post["int"], int)
    assert post["float"] == 3.5 and isinstance(post["float"], float)
    assert post["bool"] is True
    assert post["nothing"] is None
    assert post["lst"] == [1, "two", 3.0]
    assert post["nested"] == {"x": 1, "y": "two"}


def test_yaml_unquoted_date_becomes_datetime_date():
    post = frontmatter.loads(RICH)
    assert post["date"] == datetime.date(2024, 1, 15)
    assert isinstance(post["date"], datetime.date)


def test_yaml_quoted_number_stays_a_string():
    assert frontmatter.loads(RICH)["quoted"] == "42"


def test_yaml_anchors_and_aliases():
    post = frontmatter.loads("---\na: &x hello\nb: *x\n---\nc")
    assert post.metadata == {"a": "hello", "b": "hello"}


def test_yaml_round_trip_preserves_metadata_and_content():
    post = frontmatter.loads(RICH)
    repost = frontmatter.loads(frontmatter.dumps(post))
    assert repost.metadata == post.metadata
    assert repost.content == post.content


@pytest.mark.parametrize(
    "text",
    [
        "----\na: 1\n----\nx",  # four dashes still a boundary
        "--- \na: 1\n--- \nx",  # trailing space on the delimiter
        "---\na: 1\n---\nx",
    ],
)
def test_yaml_delimiter_variants(text):
    assert frontmatter.parse(text) == ({"a": 1}, "x")


def test_yaml_later_boundaries_stay_in_content():
    metadata, content = frontmatter.parse("---\na: 1\n---\npart1\n---\npart2")
    assert metadata == {"a": 1}
    assert content == "part1\n---\npart2"


def test_yaml_empty_frontmatter_block():
    assert frontmatter.parse("---\n---\nbody") == ({}, "body")


def test_yaml_export_sorts_keys_and_keeps_unicode():
    handler = YAMLHandler()
    assert handler.export({"z": 1, "a": 2}) == "a: 2\nz: 1"
    assert handler.export({"t": "中文"}) == "t: 中文"


def test_yaml_export_empty_metadata_is_flow_empty_map():
    assert YAMLHandler().export({}) == "{}"


def test_dumps_empty_post_uses_empty_map():
    assert frontmatter.dumps(frontmatter.Post("body only")) == "---\n{}\n---\n\nbody only"


def test_dumps_sort_keys_can_be_disabled():
    post = frontmatter.Post("x", b=1, a=2)
    assert frontmatter.dumps(post) == "---\na: 2\nb: 1\n---\n\nx"
    assert frontmatter.dumps(post, sort_keys=False) == "---\nb: 1\na: 2\n---\n\nx"
