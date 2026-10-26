# all the doctests here
import doctest
import frontmatter


def test_readme():
    doctest.testfile("../README.md", extraglobs={"frontmatter": frontmatter})


def test_api_docs():
    doctest.testmod(frontmatter, extraglobs={"frontmatter": frontmatter})


def test_handler_docs():
    doctest.testmod(
        frontmatter.default_handlers, extraglobs={"frontmatter": frontmatter}
    )


def test_handler_recipes():
    result = doctest.testfile("../docs/handlers.rst")
    assert result.failed == 0
