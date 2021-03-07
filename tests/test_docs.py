# all the doctests here
import doctest
import frontmatter


def test_docs():
    doctest.testfile("../README.md", extraglobs={"frontmatter": frontmatter})
    doctest.testmod(
        frontmatter.default_handlers, extraglobs={"frontmatter": frontmatter}
    )
