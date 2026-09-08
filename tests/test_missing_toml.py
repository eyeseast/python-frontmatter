"""Exercise optional TOML support in an interpreter without the dependency."""

import subprocess
import sys
import textwrap


def test_missing_toml_warning():
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent('''
            import sys
            import warnings
            sys.modules["toml"] = None
            import frontmatter

            text = '+++\\ntitle = "Hello"\\n+++\\nBody'
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                post = frontmatter.loads(text)
            assert len(caught) == 1
            assert "python-frontmatter[toml]" in str(caught[0].message)
            assert post.content == text
            assert post.metadata == {}

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                assert frontmatter.loads('---\\ntitle: Hello\\n---\\nBody')["title"] == "Hello"
                assert frontmatter.loads('Body\\n+++').content == 'Body\\n+++'
                assert frontmatter.loads('++++ text').content == '++++ text'
            assert not caught
        ''')],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
