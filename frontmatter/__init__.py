# -*- coding: utf-8 -*-
"""
Python Frontmatter: Parse and manage posts with YAML frontmatter
"""
from __future__ import unicode_literals

import codecs
import re

import six

import yaml
try:
    from yaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeDumper

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
    '---': YAMLHandler(),
    '{': JSONHandler(),
}

# if toml is installed
if TOMLHandler is not None:
    handlers['+++'] = TOMLHandler()


def parse(text, encoding='utf-8', **defaults):
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

    for delim in handlers:
        if text.startswith(delim):
            handler = handlers[delim]
            break
    else:
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


def load(fd, encoding='utf-8', **defaults):
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

    return loads(text, encoding, **defaults)


def loads(text, encoding='utf-8', **defaults):
    """
    Parse text (binary or unicode) and return a :py:class:`post <frontmatter.Post>`.

    ::

        >>> with open('tests/hello-world.markdown') as f:
        ...     post = frontmatter.loads(f.read())

    """
    metadata, content = parse(text, encoding, **defaults)
    return Post(content, **metadata)


def dump(post, fd, encoding='utf-8', **kwargs):
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
    content = dumps(post, **kwargs).encode(encoding)
    if hasattr(fd, 'write'):
        fd.write(content)

    else:
        with codecs.open(fd, 'w', encoding) as f:
            f.write(content)


def dumps(post, **kwargs):
    """
    Serialize a :py:class:`post <frontmatter.Post>` to a string and return text. 
    This always returns unicode text, which can then be encoded.

    ::

        >>> print(frontmatter.dumps(post))
        ---
        excerpt: tl;dr
        layout: post
        title: Hello, world!
        ---
        Well, hello there, world.

    """
    kwargs.setdefault('Dumper', SafeDumper)
    kwargs.setdefault('default_flow_style', False)
    
    start_delimiter = kwargs.pop('start_delimiter', '---')
    end_delimiter = kwargs.pop('end_delimiter', '---')

    metadata = yaml.dump(post.metadata, **kwargs).strip()
    metadata = u(metadata) # ensure unicode

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
    def __init__(self, content, **metadata):
        self.content = u(content)
        self.metadata = metadata

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

