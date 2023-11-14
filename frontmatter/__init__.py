# -*- coding: utf-8 -*-
"""
Python Frontmatter: Parse and manage posts with YAML frontmatter
"""
from __future__ import annotations

import codecs
import io
from typing import TYPE_CHECKING, Iterable

from .util import u
from .default_handlers import YAMLHandler, JSONHandler, TOMLHandler


if TYPE_CHECKING:
    from .default_handlers import BaseHandler


__all__ = ["parse", "load", "loads", "dump", "dumps"]


# global handlers
handlers = [
    Handler()
    for Handler in [YAMLHandler, JSONHandler, TOMLHandler]
    if Handler is not None
]


def detect_format(text: str, handlers: Iterable[BaseHandler]) -> BaseHandler | None:
    """
    Figure out which handler to use, based on metadata.
    Returns a handler instance or None.

    ``text`` should be unicode text about to be parsed.

    ``handlers`` is a dictionary where keys are opening delimiters
    and values are handler instances.
    """
    for handler in handlers:
        if handler.detect(text):
            return handler

    # nothing matched, give nothing back
    return None


def parse(
    text: str,
    encoding: str = "utf-8",
    handler: BaseHandler | None = None,
    **defaults: object,
) -> tuple[dict[str, object], str]:
    """
    Parse text with frontmatter, return metadata and content.
    Pass in optional metadata defaults as keyword args.

    If frontmatter is not found, returns an empty metadata dictionary
    (or defaults) and original text content.

    .. testsetup:: *

        >>> import frontmatter

    .. doctest::

        >>> with open('tests/yaml/hello-world.txt') as f:
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
    fm_data = handler.load(fm)
    if isinstance(fm_data, dict):
        metadata.update(fm_data)

    return metadata, content.strip()


def check(fd: str | io.IOBase, encoding: str = "utf-8") -> bool:
    """
    Check if a file-like object or filename has a frontmatter,
    return True if exists, False otherwise.

    If it contains a frontmatter but it is empty, return True as well.

    .. doctest::

        >>> frontmatter.check('tests/yaml/hello-world.txt')
        True

    """
    if hasattr(fd, "read"):
        text = fd.read()

    else:
        with codecs.open(fd, "r", encoding) as f:
            text = f.read()

    return checks(text, encoding)


def checks(text: str, encoding: str = "utf-8") -> bool:
    """
    Check if a text (binary or unicode) has a frontmatter,
    return True if exists, False otherwise.

    If it contains a frontmatter but it is empty, return True as well.

    .. doctest::

        >>> with open('tests/yaml/hello-world.txt') as f:
        ...     frontmatter.checks(f.read())
        True

    """
    text = u(text, encoding)
    return detect_format(text, handlers) != None


def load(
    fd: str | io.IOBase,
    encoding: str = "utf-8",
    handler: BaseHandler | None = None,
    **defaults: object,
) -> Post:
    """
    Load and parse a file-like object or filename,
    return a :py:class:`post <frontmatter.Post>`.

    .. doctest::

        >>> post = frontmatter.load('tests/yaml/hello-world.txt')
        >>> with open('tests/yaml/hello-world.txt') as f:
        ...     post = frontmatter.load(f)

    """
    if hasattr(fd, "read"):
        text = fd.read()

    else:
        with codecs.open(fd, "r", encoding) as f:
            text = f.read()

    handler = handler or detect_format(text, handlers)
    return loads(text, encoding, handler, **defaults)


def loads(
    text: str,
    encoding: str = "utf-8",
    handler: BaseHandler | None = None,
    **defaults: object,
) -> Post:
    """
    Parse text (binary or unicode) and return a :py:class:`post <frontmatter.Post>`.

    .. doctest::

        >>> with open('tests/yaml/hello-world.txt') as f:
        ...     post = frontmatter.loads(f.read())

    """
    text = u(text, encoding)
    handler = handler or detect_format(text, handlers)
    metadata, content = parse(text, encoding, handler, **defaults)
    return Post(content, handler, **metadata)


def dump(
    post: Post,
    fd: str | io.IOBase,
    encoding: str = "utf-8",
    handler: BaseHandler | None = None,
    **kwargs: object,
) -> None:
    """
    Serialize :py:class:`post <frontmatter.Post>` to a string and write to a file-like object.
    Text will be encoded on the way out (utf-8 by default).

    ::

        >>> from io import BytesIO
        >>> post = frontmatter.load('tests/yaml/hello-world.txt')
        >>> f = BytesIO()
        >>> frontmatter.dump(post, f)
        >>> print(f.getvalue().decode('utf-8'))
        ---
        layout: post
        title: Hello, world!
        ---
        <BLANKLINE>
        Well, hello there, world.


    .. testcode::

        from io import BytesIO
        post = frontmatter.load('tests/yaml/hello-world.txt')
        f = BytesIO()
        frontmatter.dump(post, f)
        print(f.getvalue().decode('utf-8'))

    .. testoutput::

        ---
        layout: post
        title: Hello, world!
        ---
        <BLANKLINE>
        Well, hello there, world.

    """
    content = dumps(post, handler, **kwargs)
    if hasattr(fd, "write"):
        fd.write(content.encode(encoding))

    else:
        with codecs.open(fd, "w", encoding) as f:
            f.write(content)


def dumps(post: Post, handler: BaseHandler | None = None, **kwargs: object) -> str:
    """
    Serialize a :py:class:`post <frontmatter.Post>` to a string and return text.
    This always returns unicode text, which can then be encoded.

    Passing ``handler`` will change how metadata is turned into text. A handler
    passed as an argument will override ``post.handler``, with
    :py:class:`YAMLHandler <frontmatter.default_handlers.YAMLHandler>` used as
    a default.

    ::

        >>> post = frontmatter.load('tests/yaml/hello-world.txt')
        >>> print(frontmatter.dumps(post)) # doctest: +NORMALIZE_WHITESPACE
        ---
        layout: post
        title: Hello, world!
        ---
        <BLANKLINE>
        Well, hello there, world.

    .. testcode::

        post = frontmatter.load('tests/yaml/hello-world.txt')
        print(frontmatter.dumps(post))

    .. testoutput::

        ---
        layout: post
        title: Hello, world!
        ---

        Well, hello there, world.

    """
    if handler is None:
        handler = getattr(post, "handler", None) or YAMLHandler()

    return handler.format(post, **kwargs)


class Post(object):
    """
    A post contains content and metadata from Front Matter. This is what gets
    returned by :py:func:`load <frontmatter.load>` and :py:func:`loads <frontmatter.loads>`.
    Passing this to :py:func:`dump <frontmatter.dump>` or :py:func:`dumps <frontmatter.dumps>`
    will turn it back into text.

    For convenience, metadata values are available as proxied item lookups.
    """

    def __init__(
        self, content: str, handler: BaseHandler | None = None, **metadata: object
    ) -> None:
        self.content = str(content)
        self.metadata = metadata
        self.handler = handler

    def __getitem__(self, name: str) -> object:
        "Get metadata key"
        return self.metadata[name]

    def __contains__(self, item: object) -> bool:
        "Check metadata contains key"
        return item in self.metadata

    def __setitem__(self, name: str, value: object) -> None:
        "Set a metadata key"
        self.metadata[name] = value

    def __delitem__(self, name: str) -> None:
        "Delete a metadata key"
        del self.metadata[name]

    def __bytes__(self) -> bytes:
        return self.content.encode("utf-8")

    def __str__(self) -> str:
        return self.content

    def get(self, key: str, default: object = None) -> object:
        "Get a key, fallback to default"
        return self.metadata.get(key, default)

    def keys(self) -> Iterable[str]:
        "Return metadata keys"
        return self.metadata.keys()

    def values(self) -> Iterable[object]:
        "Return metadata values"
        return self.metadata.values()

    def to_dict(self) -> dict[str, object]:
        "Post as a dict, for serializing"
        d = self.metadata.copy()
        d["content"] = self.content
        return d
