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
try:
    import toml
except ImportError:
    toml = None
import json

from .util import u

__all__ = ['parse', 'load', 'loads', 'dump', 'dumps']

POST_TEMPLATE = """\
{start_delimiter}
{metadata}
{end_delimiter}

{content}
"""


class YAMLHandler(object):
    def load(self, fm):
        return yaml.safe_load(fm)

    def split(self, text):
        FM_BOUNDARY = re.compile(r'^-{3,}$', re.MULTILINE)
        _, fm, content = FM_BOUNDARY.split(text, 2)
        return fm, content


class TOMLHandler(object):
    def load(self, fm):
        return toml.loads(fm)

    def split(self, text):
        FM_BOUNDARY = re.compile(r'^\+{3,}$', re.MULTILINE)
        _, fm, content = FM_BOUNDARY.split(text, 2)
        return fm, content


class JSONHandler(object):
    def load(self, fm):
        return json.loads(fm)

    def split(self, text):
        FM_BOUNDARY = re.compile(r'^(?:{|})$', re.MULTILINE)
        _, fm, content = FM_BOUNDARY.split(text, 2)
        return "{" + fm + "}", content


def parse(text, add_handlers=None, **defaults):
    """
    Parse text with frontmatter, return metadata and content.
    Pass in optional metadata defaults as keyword args.

    If frontmatter is not found, returns an empty metadata dictionary
    and original text content.
    """
    # ensure unicode first
    text = u(text)

    # metadata starts with defaults
    metadata = defaults.copy()

    handlers = {
        '---': YAMLHandler(),
        '{': JSONHandler(),
    }

    if toml is not None:
        handlers['+++'] = TOMLHandler()

    if add_handlers is not None:
        handlers.update(add_handlers)

    for delim in handlers:
        if text.strip().startswith(delim):
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


def load(fd, add_handlers=None, **defaults):
    """
    Load and parse a file or filename, return a post.
    """
    if hasattr(fd, 'read'):
        text = fd.read()

    else:
        with codecs.open(fd, 'r', 'utf-8') as f:
            text = f.read()

    return loads(text, add_handlers, **defaults)


def loads(text, add_handlers=None, **defaults):
    """
    Parse text and return a post.
    """
    metadata, content = parse(text, add_handlers, **defaults)
    return Post(content, **metadata)


def dump(post, fd, **kwargs):
    """
    Serialize post to a string and dump to a file-like object.
    """
    content = dumps(post, **kwargs)
    if hasattr(fd, 'write'):
        fd.write(content)

    else:
        with codecs.open(fd, 'w', 'utf-8') as f:
            f.write(content)


def dumps(post, **kwargs):
    """
    Serialize post to a string and return text.
    """
    kwargs.setdefault('Dumper', SafeDumper)
    kwargs.setdefault('default_flow_style', False)
    start_delimiter = '---'
    if 'start_delimiter' in kwargs:
        start_delimiter = kwargs['start_delimiter']
        del kwargs['start_delimiter']
    end_delimiter = '---'
    if 'end_delimiter' in kwargs:
        end_delimiter = kwargs['end_delimiter']
        del kwargs['end_delimiter']

    metadata = yaml.dump(post.metadata, **kwargs).strip()
    metadata = u(metadata) # ensure unicode
    return POST_TEMPLATE.format(
        metadata=metadata, content=post.content,
        start_delimiter=start_delimiter,
        end_delimiter=end_delimiter).strip()


class Post(object):
    """
    A post contains content and metadata from Front Matter.
    For convenience, metadata values are available as proxied item lookups. 

    Don't use this class directly. Use module-level functions load, dump, etc.
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

