"""
This is an example of setting ``sort_keys=False`` in ``frontmatter.dumps`` 
to preserve the original sort order.
"""
import frontmatter
from pathlib import Path


def test_load_sorted():
    examples = Path(__file__).parent
    text = (examples / "content" / "sorted.txt").read_text()
    post = frontmatter.loads(text)

    assert frontmatter.dumps(post, sort_keys=False) == text.strip()


if __name__ == "__main__":
    import sys
    import pytest

    pytest.main([__file__] + sys.argv[1:])
