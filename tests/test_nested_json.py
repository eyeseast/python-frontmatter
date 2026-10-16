import json

import pytest

import frontmatter
from frontmatter.default_handlers import JSONHandler


@pytest.mark.parametrize('metadata', [
    {'outer': {'inner': 1}, 'title': 'Example'},
    {'items': [{'title': 'first'}, {'title': 'second'}]},
    {'quoted': '} and {', 'nested': {'text': 'escaped " quote'}},
])
def test_nested_unindented_json_round_trip(metadata):
    post = frontmatter.Post('Body\n\n{content stays content}', JSONHandler(), **metadata)
    text = frontmatter.dumps(post, indent=0)
    restored = frontmatter.loads(text)
    assert restored.metadata == metadata
    assert restored.content == post.content


def test_malformed_delimited_json_still_raises():
    with pytest.raises(json.JSONDecodeError):
        frontmatter.loads('{\n"title": invalid\n}\n\nBody')
