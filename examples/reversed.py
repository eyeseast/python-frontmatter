import frontmatter

POST_TEMPLATE = """\
{content}

{start_delimiter}
{metadata}
{end_delimiter}
"""


class ReverseYAMLHandler(frontmatter.YAMLHandler):
    """
    This is an example of using Handler.parse and Handler.format to move Frontmatter to the bottom
    of a file, both for parsing and output.

    >>> with open("./content/reversed.txt") as f:
    ...     text = f.read()
    >>> handler = ReverseYAMLHandler()
    >>> post = frontmatter.loads(text, handler=handler)
    >>> print(post['title'])
    Front matter, reversed
    >>> print(post['ref'])
    https://github.com/eyeseast/python-frontmatter/issues/67
    >>> frontmatter.dumps(post, handler=handler) == text.strip()
    True
    """

    # FM_BOUNDARY as a string, so we can rsplit
    FM_BOUNDARY = "---"

    def split(self, text):
        """
        Split text into frontmatter and content
        """
        content, fm, _ = text.rsplit(self.FM_BOUNDARY, 2)
        return fm, content

    def format(post, **kwargs):
        start_delimiter = kwargs.pop("start_delimiter", handler.START_DELIMITER)
        end_delimiter = kwargs.pop("end_delimiter", handler.END_DELIMITER)
        metadata = self.export(post.metadata, **kwargs)

        return POST_TEMPLATE.format(
            content=post.content,
            metadata=metadata,
            start_delimiter=start_delimiter,
            end_delimiter=end_delimiter,
        ).strip()


if __name__ == "__main__":
    import doctest

    doctest.testmod()