# -*- coding: utf-8 -*-
"""
Python Frontmatter: Parse and manage posts with YAML frontmatter
"""
from __future__ import unicode_literals

import codecs
import re

import six

from .util import u
from .default_handlers import YAMLHandler, JSONHandler, TOMLHandler


__all__ = ['parse', 'load', 'loads', 'dump', 'dumps']

POST_TEMPLATE = """\
{start_delimiter}
{metadata}
{end_delimiter}

{content}
"""

# global handlers
handlers = {
    Handler.FM_BOUNDARY: Handler() 
    for Handler in [YAMLHandler, JSONHandler, TOMLHandler]
    if Handler is not None
}


def detect_format(text, handlers):
    """
    Figure out which handler to use, based on metadata.
    Returns a handler instance or None.

    ``text`` should be unicode text about to be parsed.

    ``handlers`` is a dictionary where keys are opening delimiters 
    and values are handler instances.
    """
    for pattern, handler in handlers.items():
        if pattern.match(text):
            return handler

    # nothing matched, give nothing back
    return None


def parse(text, encoding='utf-8', handler=None, **defaults):
    """
    Parse text with frontmatter, return metadata and content.
    Pass in optional metadata defaults as keyword args.

    If frontmatter is not found, returns an empty metadata dictionary
    (or defaults) and original text content.

    ::

        >>> with open('tests/hello-world.markdown') as f:
        ...     metadata, content = frontmatter.parse(f.read())
        >>> print(metadata['title'])
        Hello, world!

    """
    # ensure unicode first
    text = u(text, encoding).strip()

    # metadata starts with defaults
    metadata = defaults.copy()

    # this will only run if a handler hasn't been set higher up
    handler = handler or detect_format(text, handlers)
    if handler is None:
        return metadata, text

    # split on the delimiters
    try:
        fm, content = handler.split(text)
    except ValueError:
        # if we can't split, bail
        return metadata, text

    # parse, now that we have frontmatter
    fm = handler.load(fm)
    if isinstance(fm, dict):
        metadata.update(fm)

    return metadata, content.strip()


def load(fd, encoding='utf-8', handler=None, **defaults):
    """
    Load and parse a file-like object or filename, 
    return a :py:class:`post <frontmatter.Post>`.

    ::

        >>> post = frontmatter.load('tests/hello-world.markdown')
        >>> with open('tests/hello-world.markdown') as f:
        ...     post = frontmatter.load(f)

    """
    if hasattr(fd, 'read'):
        text = fd.read()

    else:
        with codecs.open(fd, 'r', encoding) as f:
            text = f.read()

    handler = handler or detect_format(text, handlers)
    return loads(text, encoding, handler, **defaults)


def loads(text, encoding='utf-8', handler=None, **defaults):
    """
    Parse text (binary or unicode) and return a :py:class:`post <frontmatter.Post>`.

    ::

        >>> with open('tests/hello-world.markdown') as f:
        ...     post = frontmatter.loads(f.read())

    """
    text = u(text, encoding)
    handler = handler or detect_format(text, handlers)
    metadata, content = parse(text, encoding, handler, **defaults)
    return Post(content, handler, **metadata)


def dump(post, fd, encoding='utf-8', handler=None, **kwargs):
    """
    Serialize :py:class:`post <frontmatter.Post>` to a string and write to a file-like object.
    Text will be encoded on the way out (utf-8 by default).

    ::

        >>> from io import StringIO
        >>> f = StringIO()
        >>> frontmatter.dump(post, f)
        >>> print(f.getvalue())
        ---
        excerpt: tl;dr
        layout: post
        title: Hello, world!
        ---
        Well, hello there, world.


    """
    content = dumps(post, handler, **kwargs).encode(encoding)
    if hasattr(fd, 'write'):
        fd.write(content)

    else:
        with codecs.open(fd, 'w', encoding) as f:
            f.write(content)


def dumps(post, handler=None, **kwargs):
    """
    Serialize a :py:class:`post <frontmatter.Post>` to a string and return text. 
    This always returns unicode text, which can then be encoded.

    Passing ``handler`` will change how metadata is turned into text. A handler
    passed as an argument will override ``post.handler``, with 
    :py:class:`YAMLHandler <frontmatter.default_handlers.YAMLHandler>` used as 
    a default.
    ::

        >>> print(frontmatter.dumps(post))
        ---
        excerpt: tl;dr
        layout: post
        title: Hello, world!
        ---
        Well, hello there, world.

    """
    if handler is None:
        handler = getattr(post, 'handler', None) or YAMLHandler()

    start_delimiter = kwargs.pop('start_delimiter', handler.START_DELIMITER)
    end_delimiter = kwargs.pop('end_delimiter', handler.END_DELIMITER)

    metadata = handler.export(post.metadata, **kwargs)

    return POST_TEMPLATE.format(
        metadata=metadata, content=post.content,
        start_delimiter=start_delimiter,
        end_delimiter=end_delimiter).strip()


class Post(object):
    """
    A post contains content and metadata from Front Matter. This is what gets
    returned by :py:func:`load <frontmatter.load>` and :py:func:`loads <frontmatter.loads>`. 
    Passing this to :py:func:`dump <frontmatter.dump>` or :py:func:`dumps <frontmatter.dumps>` 
    will turn it back into text.

    For convenience, metadata values are available as proxied item lookups. 
    """
    def __init__(self, content, handler=None, **metadata):
        self.content = u(content)
        self.metadata = metadata
        self.handler = handler

    def __getitem__(self, name):
        "Get metadata key"
        return self.metadata[name]        

    def __setitem__(self, name, value):
        "Set a metadata key"
        self.metadata[name] = value

    def __delitem__(self, name):
        "Delete a metadata key"
        del self.metadata[name]

    def __bytes__(self):
        return self.content.encode('utf-8')

    def __str__(self):
        if six.PY2:
            return self.__bytes__()
        return self.content

    def __unicode__(self):
        return self.content

    def get(self, key, default=None):
        "Get a key, fallback to default"
        return self.metadata.get(key, default)

    def keys(self):
        "Return metadata keys"
        return self.metadata.keys()

    def values(self):
        "Return metadata values"
        return self.metadata.values()

    def to_dict(self):
        "Post as a dict, for serializing"
        d = self.metadata.copy()
        d['content'] = self.content
        return d

