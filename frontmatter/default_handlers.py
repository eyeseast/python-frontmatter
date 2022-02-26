# -*- coding: utf-8 -*-
"""
.. testsetup:: handlers

    import frontmatter

By default, ``frontmatter`` reads and writes YAML metadata. But maybe
you don't like YAML. Maybe enjoy writing metadata in JSON, or TOML, or
some other exotic markup not yet invented. For this, there are handlers.

This module includes handlers for YAML, JSON and TOML, as well as a 
:py:class:`BaseHandler <frontmatter.default_handlers.BaseHandler>` that 
outlines the basic API and can be subclassed to deal with new formats.

**Note**: The TOML handler is only available if the `toml <https://pypi.org/project/toml/>`_
library is installed.

Handlers
--------

Handlers do most of the underlying work parsing and exporting front matter.
When you call :py:func:`frontmatter.loads <frontmatter.loads>`, frontmatter first needs to figure out the
best handler for the format you're using (YAML, JSON, TOML, etc), then call
methods to read or write metadata.

A handler needs to do four things:

- detect whether it can parse the given piece of text
- split front matter from content, returning both as a two-tuple
- parse front matter into a Python dictionary
- export a dictionary back into text

An example:

Calling :py:func:`frontmatter.load <frontmatter.load>` (or :py:func:`loads <frontmatter.loads>`) 
with the ``handler`` argument tells frontmatter which handler to use. 
The handler instance gets saved as an attribute on the returned post 
object. By default, calling :py:func:`frontmatter.dumps <frontmatter.dumps>` 
on the post will use the attached handler.


::

    >>> import frontmatter
    >>> from frontmatter.default_handlers import YAMLHandler, TOMLHandler
    >>> post = frontmatter.load('tests/toml/hello-toml.md', handler=TOMLHandler())
    >>> post.handler #doctest: +ELLIPSIS
    <frontmatter.default_handlers.TOMLHandler object at 0x...>

    >>> print(frontmatter.dumps(post)) # doctest: +SKIP
    +++
    test = "tester"
    something = "else"
    author = "bob"
    +++
    <BLANKLINE>
    Title
    =====
    <BLANKLINE>
    title2
    ------
    <BLANKLINE>
    Hello.
    <BLANKLINE>
    Just need three dashes
    ---
    <BLANKLINE>
    And this shouldn't break.

Passing a new handler to :py:func:`frontmatter.dumps <frontmatter.dumps>` 
(or :py:func:`dump <frontmatter.dump>`) changes the export format:

::

    >>> print(frontmatter.dumps(post, handler=YAMLHandler())) # doctest: +NORMALIZE_WHITESPACE
    ---
    author: bob
    something: else
    test: tester
    ---
    <BLANKLINE>
    Title
    =====
    <BLANKLINE>
    title2
    ------
    <BLANKLINE>
    Hello.
    <BLANKLINE>
    Just need three dashes
    ---
    <BLANKLINE>
    And this shouldn't break.

Changing the attached ``handler`` on a post has the same effect. Setting ``handler``
to ``None`` will default the post back to :py:class:`YAMLHandler <frontmatter.default_handlers.YAMLHandler>`.
These three variations will produce the same export:

::

    # set YAML format when dumping, but the old handler attached
    >>> t1 = frontmatter.dumps(post, handler=YAMLHandler())
    >>> post.handler = YAMLHandler() # set a new handler, changing all future exports
    >>> t2 = frontmatter.dumps(post)
    >>> post.handler = None # remove handler, defaulting back to YAML
    >>> t3 = frontmatter.dumps(post)
    >>> t1 == t2 == t3
    True

All handlers use the interface defined on ``BaseHandler``. Each handler needs to know how to:

- split metadata and content, based on a boundary pattern (``handler.split``)
- parse plain text metadata into a Python dictionary (``handler.load``)
- export a dictionary back into plain text (``handler.export``)
- format exported metadata and content into a single string (``handler.format``)


"""

import json
import re
import yaml

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper
    from yaml import SafeLoader

try:
    import toml
except ImportError:
    toml = None

from .util import u


__all__ = ["BaseHandler", "YAMLHandler", "JSONHandler"]

if toml:
    __all__.append("TOMLHandler")


DEFAULT_POST_TEMPLATE = """\
{start_delimiter}
{metadata}
{end_delimiter}

{content}
"""


class BaseHandler:
    """
    BaseHandler lays out all the steps to detecting, splitting, parsing and
    exporting front matter metadata.

    All default handlers are subclassed from BaseHandler.
    """

    FM_BOUNDARY = None
    START_DELIMITER = None
    END_DELIMITER = None

    def __init__(self, fm_boundary=None, start_delimiter=None, end_delimiter=None):
        self.FM_BOUNDARY = fm_boundary or self.FM_BOUNDARY
        self.START_DELIMITER = start_delimiter or self.START_DELIMITER
        self.END_DELIMITER = end_delimiter or self.END_DELIMITER

        if self.FM_BOUNDARY is None:
            raise NotImplementedError(
                "No frontmatter boundary defined. "
                "Please set {}.FM_BOUNDARY to a regular expression".format(
                    self.__class__.__name__
                )
            )

    def detect(self, text):
        """
        Decide whether this handler can parse the given ``text``,
        and return True or False.

        Note that this is *not* called when passing a handler instance to
        :py:func:`frontmatter.load <frontmatter.load>` or :py:func:`loads <frontmatter.loads>`.
        """
        if self.FM_BOUNDARY.match(text):
            return True
        return False

    def split(self, text):
        """
        Split text into frontmatter and content
        """
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return fm, content

    def load(self, fm):
        """
        Parse frontmatter and return a dict
        """
        raise NotImplementedError

    def export(self, metadata, **kwargs):
        """
        Turn metadata back into text
        """
        raise NotImplementedError

    def format(self, post, **kwargs):
        """
        Turn a post into a string, used in ``frontmatter.dumps``
        """
        start_delimiter = kwargs.pop("start_delimiter", self.START_DELIMITER)
        end_delimiter = kwargs.pop("end_delimiter", self.END_DELIMITER)

        metadata = self.export(post.metadata, **kwargs)

        return DEFAULT_POST_TEMPLATE.format(
            metadata=metadata,
            content=post.content,
            start_delimiter=start_delimiter,
            end_delimiter=end_delimiter,
        ).strip()


class YAMLHandler(BaseHandler):
    """
    Load and export YAML metadata. By default, this handler uses YAML's
    "safe" mode, though it's possible to override that.
    """

    FM_BOUNDARY = re.compile(r"^-{3,}\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = "---"

    def load(self, fm, **kwargs):
        """
        Parse YAML front matter. This uses yaml.SafeLoader by default.
        """
        kwargs.setdefault("Loader", SafeLoader)
        return yaml.load(fm, **kwargs)

    def export(self, metadata, **kwargs):
        """
        Export metadata as YAML. This uses yaml.SafeDumper by default.
        """
        kwargs.setdefault("Dumper", SafeDumper)
        kwargs.setdefault("default_flow_style", False)
        kwargs.setdefault("allow_unicode", True)

        metadata = yaml.dump(metadata, **kwargs).strip()
        return u(metadata)  # ensure unicode


class JSONHandler(BaseHandler):
    """
    Load and export JSON metadata.

    Note that changing ``START_DELIMITER`` or ``END_DELIMITER`` may break JSON parsing.
    """

    FM_BOUNDARY = re.compile(r"^(?:{|})$", re.MULTILINE)
    START_DELIMITER = ""
    END_DELIMITER = ""

    def split(self, text):
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return "{" + fm + "}", content

    def load(self, fm, **kwargs):
        return json.loads(fm, **kwargs)

    def export(self, metadata, **kwargs):
        "Turn metadata into JSON"
        kwargs.setdefault("indent", 4)
        metadata = json.dumps(metadata, **kwargs)
        return u(metadata)


if toml:

    class TOMLHandler(BaseHandler):
        """
        Load and export TOML metadata.

        By default, split based on ``+++``.
        """

        FM_BOUNDARY = re.compile(r"^\+{3,}\s*$", re.MULTILINE)
        START_DELIMITER = END_DELIMITER = "+++"

        def load(self, fm, **kwargs):
            return toml.loads(fm, **kwargs)

        def export(self, metadata, **kwargs):
            "Turn metadata into TOML"
            metadata = toml.dumps(metadata)
            return u(metadata)


else:
    TOMLHandler = None
