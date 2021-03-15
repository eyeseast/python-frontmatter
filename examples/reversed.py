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

    >>> with open("examples/content/reversed.txt") as f:
    ...     text = f.read()
    >>> handler = ReverseYAMLHandler()
    >>> post = frontmatter.loads(text, handler=handler)
    >>> print(post['title'])
    Front matter, reversed
    >>> print(post['ref'])
    https://github.com/eyeseast/python-frontmatter/issues/67
    >>> print(frontmatter.dumps(post, handler=handler))
    This is txt format to prevent reformatting
    ============================================
    <BLANKLINE>
    Dextra tempore deus
    -------------------
    <BLANKLINE>
    Lorem markdownum est dicere pariter es dat si non, praesignis Styge, non
    Maenalon magnae miserrimus. Corpora frustra committere insuetum et fecit
    **Hippothousque arbore solio** inopem utraque concepit illa comantem me mortis
    epulis protinus putares! Piceis *manibus*. Erinys et parum morsusque repugnat
    ore corna sacris, pollice movet currus gestamina.
    <BLANKLINE>
    Genitoris forti circumfuso videbit fertur vulnere simillima
    -----------------------------------------------------------
    <BLANKLINE>
    Audit enim, est illa nervis loco inque hoc, et rigido! Monstris vatibus laetos
    contemptor Calydonia. Et visa capillo referens regia: usus: odiique nostro.
    **Vim** sensit inpulit virginis metuens secum cogit, corpus.
    <BLANKLINE>
    Humus ater Dromas est honorem, Titanida glandibus sinit, e terras capillos
    cremet retinentibus male. Tertia et cedit eliso flectere haec, cute nihil
    marmore armo. Mihi [Olympi](http://que.org/saepepoenas), iam sustinet addidit
    humana similis.
    <BLANKLINE>
    ---
    ref: https://github.com/eyeseast/python-frontmatter/issues/67
    title: Front matter, reversed
    ---
    """

    # FM_BOUNDARY as a string, so we can rsplit
    FM_BOUNDARY = "---"

    def split(self, text):
        """
        Split text into frontmatter and content
        """
        content, fm, _ = text.rsplit(self.FM_BOUNDARY, 2)
        return fm, content

    def format(self, post, **kwargs):
        start_delimiter = kwargs.pop("start_delimiter", self.START_DELIMITER)
        end_delimiter = kwargs.pop("end_delimiter", self.END_DELIMITER)
        metadata = self.export(post.metadata, **kwargs)

        return POST_TEMPLATE.format(
            content=post.content,
            metadata=metadata,
            start_delimiter=start_delimiter,
            end_delimiter=end_delimiter,
        ).strip()
