# -*- coding: utf-8 -*-
"""
Python Frontmatter: Parse and manage posts with YAML frontmatter
"""
from __future__ import unicode_literals

import codecs

import six
import yaml

try:
    from yaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeDumper

from .util import u

__all__ = ['parse', 'load', 'loads', 'dump', 'dumps']

POST_TEMPLATE = """\
---
{metadata}
---

{content}
"""


def parse(text, **defaults):
    """
    Parse text with YAML frontmatter, return metadata and content.
    Pass in optional metadata defaults as keyword args.

    If frontmatter is not found, returns an empty metadata dictionary
    and original text content.
    """
    # ensure unicode first
    text = u(text)

    # metadata starts with defaults
    metadata = defaults.copy()

    # metadata text starts with three dashes and ends with three dashes or three dots
    lines = text.splitlines(True)
    i_start = i_end = -1
    for i, line in enumerate(lines):
        if (i_start==-1 and line.rstrip()=='---'):
            i_start = i
        elif (i_start!=-1 and line.rstrip() in ('---', '...')):
            i_end = i
            break

    if i_end==-1: # if we can't split, bail
        return metadata, text
    else:
        fm = ''.join(lines[i_start+1:i_end])
        content = ''.join(lines[i_end+1:])

    # parse yaml, now that we have frontmatter
    fm = yaml.safe_load(fm)
    if isinstance(fm, dict):
        metadata.update(fm)

    return metadata, content.strip()


def load(fd, **defaults):
    """
    Load and parse a file or filename, return a post.
    """
    if hasattr(fd, 'read'):
        text = fd.read()

    else:
        with codecs.open(fd, 'r', 'utf-8') as f:
            text = f.read()

    return loads(text, **defaults)


def loads(text, **defaults):
    """
    Parse text and return a post.
    """
    metadata, content = parse(text, **defaults)
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

    metadata = yaml.dump(post.metadata, **kwargs).strip()
    metadata = u(metadata) # ensure unicode
    return POST_TEMPLATE.format(metadata=metadata, content=post.content).strip()


class Post(object):
    """
    A post contains content and metadata from YAML Front Matter.
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

