import frontmatter


class PandocHandler(frontmatter.YAMLHandler):
    """
    Pandoc format uses different start and end delimiters, which trips up parsing a bit.
    To make it work, we need a custom handler that deals with each part separately.

    >>> with open('examples/content/pandoc.txt') as f:
    ...     text = f.read()
    >>> post = frontmatter.loads(text, handler=PandocHandler())
    >>> post['title']
    'Pandoc-flavored Front Matter'
    >>> print(frontmatter.dumps(post))
    ---
    lipsum: https://www.lipsum.com/
    ref: https://github.com/eyeseast/python-frontmatter/issues/42
    title: Pandoc-flavored Front Matter
    ...
    <BLANKLINE>
    Nulla pulvinar, turpis ullamcorper tempus posuere, sapien purus porttitor diam, id ullamcorper lorem neque id mauris. Sed facilisis, elit eget luctus posuere, quam nibh imperdiet magna, vel placerat arcu risus sit amet arcu. Morbi sit amet mollis leo. Mauris sit amet condimentum mi. Quisque lectus libero, varius scelerisque tempor ut, elementum ac diam. Morbi nisl sapien, ullamcorper ac elementum at, auctor quis magna. Curabitur nec neque purus.
    <BLANKLINE>
    Proin tincidunt cursus turpis, mattis euismod sapien. Cras consectetur id felis non volutpat. Proin vulputate ante gravida quam euismod blandit. Nulla at varius nibh. Donec congue erat vel mattis volutpat. Sed fringilla lorem sit amet velit ornare gravida. Sed ac scelerisque nisi.
    <BLANKLINE>
    Generated 2 paragraphs, 109 words, 730 bytes of Lorem Ipsum
    """

    START_DELIMITER = "---"
    END_DELIMITER = "..."

    def split(self, text):
        "It's going to take a few passes to split here"
        _, start, text = text.partition(self.START_DELIMITER)
        fm, end, content = text.partition(self.END_DELIMITER)
        return fm, content
