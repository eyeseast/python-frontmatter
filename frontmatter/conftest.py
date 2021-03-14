import pytest


@pytest.fixture(autouse=True)
def add_globals(doctest_namespace):
    import frontmatter

    doctest_namespace["frontmatter"] = frontmatter
