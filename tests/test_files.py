"""
Test individual files with frontmatter against expected results.
Files should be in a subdirectory under `tests`, usually sorted by format (yaml, toml, json).

For a file called hello-world.markdown, there should be a corresponding file called hello-world.json
matching the expected output.
"""
import os
import json
from itertools import chain
from pathlib import Path

import frontmatter
import pytest


def files():
    tests = Path(__file__).parent
    md = tests.glob("**/*.md")
    txt = tests.glob("**/*.txt")
    return chain(md, txt)


def get_result_filename(path):
    root, ext = os.path.splitext(path)
    return f"{root}.result.json"


@pytest.mark.parametrize("filename", list(files()))
def test_can_parse(filename):
    "Check we can load every file in our test directories without raising an error"
    for filename in files():
        post = frontmatter.load(filename)
        assert isinstance(post, frontmatter.Post)


@pytest.mark.parametrize("filename", list(files()))
def test_file(filename):
    result = Path(get_result_filename(filename))
    if not result.exists():
        pytest.fail(f"{result.name} does not exist")

    post = frontmatter.load(filename)
    result = json.loads(result.read_text())

    assert post.to_dict() == result