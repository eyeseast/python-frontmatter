"""
By default, ``frontmatter`` reads and writes YAML metadata. But maybe
you don't like YAML. Maybe enjoy writing metadata in JSON, or TOML, or
some other exotic markup not yet invented. For this, there are handlers.

This module includes handlers for YAML, JSON and TOML, as well as a 
:py:class:`BaseHandler <frontmatter.default_handlers.BaseHandler>` that 
outlines the basic API and can be subclassed to deal with new formats.

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
    >>> post = frontmatter.load('tests/hello-toml.markdown', handler=TOMLHandler())
    >>> post.handler #doctest: +ELLIPSIS
    <frontmatter.default_handlers.TOMLHandler object at 0x...>

    >>> print(frontmatter.dumps(post)) # doctest: +NORMALIZE_WHITESPACE
    +++
    test = "tester"
    author = "bob"
    something = "else"
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
    test: tester
    author: bob
    something: else
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

    # set a new handler, changing all future exports
    >>> post.handler = YAMLHandler()
    >>> t2 = frontmatter.dumps(post)

    # remove handler, defaulting back to YAML
    >>> post.handler = None
    >>> t3 = frontmatter.dumps(post)

    >>> t1 == t2 == t3
    True

"""
from __future__ import unicode_literals

import json
import re
import yaml

try:
    import toml
except ImportError:
    toml = None


__all__ = ['BaseHandler', 'YAMLHandler', 'JSONHandler']

if toml:
    __all__.append('TOMLHandler')


class BaseHandler(object):

    FM_BOUNDARY = None

    def __init__(self, fm_boundary=None):
        self.FM_BOUNDARY = fm_boundary or self.FM_BOUNDARY

        if self.FM_BOUNDARY is None:
            raise NotImplementedError('No frontmatter boundary defined. '
                'Please set {}.FM_BOUNDARY to a regular expression'.format(self.__class__.__name__))

    def detect(self, text):
        """
        Decide whether this handler can parse the given ``text``,
        and return True or False.

        Note that this is *not* called when passing a handler instance to 
        :py:func:`frontmatter.load <frontmatter.load>` or :py:func:`loads <frontmatter.loads>`.
        """
        raise NotImplementedError

    def load(self, fm):
        """
        Parse frontmatter and return a dict
        """
        raise NotImplementedError

    def split(self, text):
        """
        Split text into frontmatter and content
        """
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return fm, content


class YAMLHandler(BaseHandler):
    FM_BOUNDARY = re.compile(r'^-{3,}$', re.MULTILINE)

    def load(self, fm, **kwargs):
        return yaml.safe_load(fm, **kwargs)


class JSONHandler(BaseHandler):
    FM_BOUNDARY = re.compile(r'^(?:{|})$', re.MULTILINE)

    def load(self, fm, **kwargs):
        return json.loads(fm, **kwargs)

    def split(self, text):
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return "{" + fm + "}", content


if toml:
    class TOMLHandler(BaseHandler):
        FM_BOUNDARY = re.compile(r'^\+{3,}$', re.MULTILINE)

        def load(self, fm, **kwargs):
            return toml.loads(fm, **kwargs)

else:
    TOMLHandler = None