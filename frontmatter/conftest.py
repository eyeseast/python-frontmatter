from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def add_globals(doctest_namespace: dict[str, object]) -> None:
    import frontmatter

    doctest_namespace["frontmatter"] = frontmatter
