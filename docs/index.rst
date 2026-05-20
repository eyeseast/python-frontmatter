.. Frontmatter documentation master file, created by
   sphinx-quickstart on Thu Jul 21 21:54:42 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python Frontmatter
=====================

.. module:: frontmatter

`Front matter <https://docs.github.com/en/contributing/writing-for-github-docs/using-yaml-frontmatter>`__
offers a useful way to add arbitrary, structured metadata to text
documents, regardless of type.

This is a small package to load and parse files (or just text) with YAML
(or JSON, TOML or other) front matter.


Install
--------

.. code-block:: shell

    # with pip
    pip install python-frontmatter

    # or uv
    uv add python-frontmatter

    # local development, with uv
    uv sync

Usage
------

::

    >>> import frontmatter

Load a post from a filename:

::

    >>> post = frontmatter.load('tests/yaml/hello-world.txt')

Or a file (or file-like object):

::

    >>> with open('tests/yaml/hello-world.txt') as f:
    ...     post = frontmatter.load(f)

Or load from text:

::

    >>> with open('tests/yaml/hello-world.txt') as f:
    ...     post = frontmatter.loads(f.read())

If the file has a `Byte-Order Mark <https://en.wikipedia.org/wiki/Byte_order_mark>`__
(BOM), strip it off first. An easy way to do this is by using the
`utf-8-sig <https://docs.python.org/3/library/codecs.html?highlight=utf%208%20sig#module-encodings.utf_8_sig>`__
encoding:

::

    >>> with open('tests/yaml/hello-world.txt', encoding="utf-8-sig") as f:
    ...     post = frontmatter.load(f)

Access content:

::

    >>> print(post.content)
    Well, hello there, world.

    # this works, too
    >>> print(post)
    Well, hello there, world.

Use metadata (metadata gets proxied as post keys):

::

    >>> print(post['title'])
    Hello, world!

Metadata is a dictionary, with some handy proxies:

::

    >>> sorted(post.keys())
    ['layout', 'title']

    >>> from pprint import pprint
    >>> post['excerpt'] = 'tl;dr'
    >>> pprint(post.metadata)
    {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'}

If you don't need the whole post object, use `frontmatter.parse` to return metadata and content separately:

::

    >>> with open('tests/yaml/hello-world.txt') as f:
    ...     metadata, content = frontmatter.parse(f.read())
    >>> print(metadata['title'])
    Hello, world!

Write back to plain text, too:

::

    >>> print(frontmatter.dumps(post))
    ---
    excerpt: tl;dr
    layout: post
    title: Hello, world!
    ---
    Well, hello there, world.

Or write to a file (or file-like object):

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

For more examples, see files in the ``tests/`` directory. Each sample
file has a corresponding ``.result.json`` file showing the expected
parsed output. See also the ``examples/`` directory, which covers more
ways to customize input and output.


.. toctree::
   :maxdepth: 2

   handlers
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

