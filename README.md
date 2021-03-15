# Python Frontmatter

[Jekyll](http://jekyllrb.com/)-style YAML front matter offers a useful way to add arbitrary, structured metadata to text documents, regardless of type.

This is a small package to load and parse files (or just text) with YAML (or JSON, TOML or other) front matter.

[![Tests](https://github.com/eyeseast/feed-to-sqlite/workflows/Test/badge.svg)](https://github.com/eyeseast/feed-to-sqlite/actions?query=workflow%3ATest)
[![PyPI](https://img.shields.io/pypi/v/python-frontmatter.svg)](https://pypi.org/project/python-frontmatter/)

**[Documentation](https://python-frontmatter.readthedocs.io/en/latest/)**

## Install:

    pip install python-frontmatter

## Usage:

```python
>>> import frontmatter

```

Load a post from a filename:

```python
>>> post = frontmatter.load('tests/yaml/hello-world.txt')

```

Or a file (or file-like object):

```python
>>> with open('tests/yaml/hello-world.txt') as f:
...     post = frontmatter.load(f)

```

Or load from text:

```python
>>> with open('tests/yaml/hello-world.txt') as f:
...     post = frontmatter.loads(f.read())

```

Access content:

```python
>>> print(post.content)
Well, hello there, world.

# this works, too
>>> print(post)
Well, hello there, world.

```

Use metadata (metadata gets proxied as post keys):

```python
>>> print(post['title'])
Hello, world!

```

Metadata is a dictionary, with some handy proxies:

```python
>>> sorted(post.keys())
['layout', 'title']

>>> from pprint import pprint
>>> post['excerpt'] = 'tl;dr'
>>> pprint(post.metadata)
{'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'}

```

If you don't need the whole post object, just parse:

```python
>>> with open('tests/yaml/hello-world.txt') as f:
...     metadata, content = frontmatter.parse(f.read())
>>> print(metadata['title'])
Hello, world!

```

Write back to plain text, too:

```python
>>> print(frontmatter.dumps(post)) # doctest: +NORMALIZE_WHITESPACE
---
excerpt: tl;dr
layout: post
title: Hello, world!
---
Well, hello there, world.

```

Or write to a file (or file-like object):

```python
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

```

For more examples, see files in the `tests/` directory. Each sample file has a corresponding `.result.json` file showing the expected parsed output. See also the `examples/` directory, which covers more ways to customize input and output.
