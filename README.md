Python Frontmatter
==================

[Jekyll](http://jekyllrb.com/)-style YAML front matter offers a useful way to add arbitrary, structured metadata to text documents, regardless of type.

This is a small package to load and parse files (or just text) with YAML front matter.

[![Build Status](https://travis-ci.org/eyeseast/python-frontmatter.svg?branch=master)](https://travis-ci.org/eyeseast/python-frontmatter)

Install:
--------

    pip install python-frontmatter


Usage:
------

    >>> import frontmatter

Load a post from a filename:

    >>> post = frontmatter.load('tests/hello-world.markdown')

Or a file (or file-like object):

    >>> with open('tests/hello-world.markdown') as f:
    ...     post = frontmatter.load(f)

Or load from text:

    >>> with open('tests/hello-world.markdown') as f:
    ...     post = frontmatter.loads(f.read())

Access content:

    >>> print(post.content)
    Well, hello there, world.

    # this works, too
    >>> print(post)
    Well, hello there, world.


Use metadata (metadata gets proxied as post keys):

    >>> print(post['title'])
    Hello, world!

Metadata is a dictionary, with some handy proxies:

    >>> sorted(post.keys())
    ['layout', 'title']

    >>> from pprint import pprint
    >>> post['excerpt'] = 'tl;dr'
    >>> pprint(post.metadata)
    {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'}

If you don't need the whole post object, just parse:

    >>> with open('tests/hello-world.markdown') as f:
    ...     metadata, content = frontmatter.parse(f.read())
    >>> print(metadata['title'])
    Hello, world!

Write back to plain text, too:

    >>> print(frontmatter.dumps(post)) # doctest: +NORMALIZE_WHITESPACE
    ---
    excerpt: tl;dr
    layout: post
    title: Hello, world!
    ---
    Well, hello there, world.

Or write to a file (or file-like object):

    >>> from io import BytesIO
    >>> f = BytesIO()
    >>> frontmatter.dump(post, f)
    >>> print(f.getvalue().decode('utf-8')) # doctest: +NORMALIZE_WHITESPACE
    ---
    excerpt: tl;dr
    layout: post
    title: Hello, world!
    ---
    Well, hello there, world.


