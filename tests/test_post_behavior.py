"""Tests for frontmatter.Post: the metadata mapping protocol and helpers."""

import pytest

import frontmatter
from frontmatter import Post


@pytest.fixture
def post():
    return Post("content here", title="T", n=1)


def test_content_and_metadata_stored(post):
    assert post.content == "content here"
    assert post.metadata == {"title": "T", "n": 1}
    assert post.handler is None


def test_getitem_and_contains(post):
    assert post["title"] == "T"
    assert "title" in post
    assert "missing" not in post


def test_getitem_missing_raises_key_error(post):
    with pytest.raises(KeyError):
        post["missing"]


def test_setitem_and_delitem(post):
    post["new"] = 5
    assert post.metadata["new"] == 5
    del post["new"]
    assert "new" not in post
    with pytest.raises(KeyError):
        del post["new"]


def test_get_with_default(post):
    assert post.get("title") == "T"
    assert post.get("nope") is None
    assert post.get("nope", 42) == 42


def test_keys_and_values(post):
    assert sorted(post.keys()) == ["n", "title"]
    assert sorted(post.values(), key=str) == [1, "T"]


def test_to_dict_adds_content_and_returns_a_copy(post):
    d = post.to_dict()
    assert d == {"title": "T", "n": 1, "content": "content here"}
    d["title"] = "mutated"
    d["content"] = "mutated"
    assert post["title"] == "T"
    assert post.content == "content here"


def test_str_and_bytes_are_the_content(post):
    assert str(post) == "content here"
    assert bytes(post) == "content here".encode("utf-8")


def test_content_is_coerced_to_str():
    assert Post(123).content == "123"
    # quirk: None is stringified too, not treated as empty
    assert Post(None).content == "None"


def test_post_without_handler_dumps_as_yaml():
    assert frontmatter.dumps(Post("x", a=1)) == "---\na: 1\n---\n\nx"


def test_setting_handler_to_none_restores_yaml_default():
    post = frontmatter.loads('{\n"a": 1\n}\nx')
    assert post.handler is not None
    post.handler = None
    assert frontmatter.dumps(post) == "---\na: 1\n---\n\nx"
