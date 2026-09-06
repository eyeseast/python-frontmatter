Customizing input and output
============================

.. automodule:: frontmatter.default_handlers

.. autoclass:: frontmatter.default_handlers.BaseHandler
    :members: 

.. autoclass:: frontmatter.default_handlers.YAMLHandler

.. autoclass:: frontmatter.default_handlers.JSONHandler

.. autoclass:: frontmatter.default_handlers.TOMLHandler

Indenting YAML sequences
------------------------

With the YAML handler, keyword arguments to :py:func:`frontmatter.dumps`
are passed through ``YAMLHandler.export`` to ``yaml.dump``. For example,
``indent=4`` indents nested mappings by four spaces. By default, PyYAML writes
block sequences without extra indentation: the ``-`` aligns with the key
above it. Increasing ``indent`` alone does not change these indentless sequences.

To indent sequence items too, pass a subclass of ``yaml.SafeDumper`` that
disables indentless sequences. Use this Python dumper explicitly, even when
LibYAML is installed: ``yaml.CSafeDumper`` does not call the Python
``increase_indent`` method. Subclassing ``yaml.SafeDumper`` retains safe
serialisation, without support for arbitrary Python objects.

.. doctest:: yaml-indentation
    :options: -NORMALIZE_WHITESPACE

    >>> import frontmatter
    >>> import yaml
    >>> class IndentedSafeDumper(yaml.SafeDumper):
    ...     def increase_indent(self, flow=False, indentless=False):
    ...         return super().increase_indent(flow, False)
    >>> post = frontmatter.loads("""\
    ... ---
    ... date: 2023-05-12
    ... title: Sample
    ... tags:
    ...     - test
    ...     - sample
    ... nested:
    ...     tags:
    ...         - nested
    ... ---
    ...
    ... # Title 1
    ... """)
    >>> text = frontmatter.dumps(
    ...     post, Dumper=IndentedSafeDumper, indent=4, sort_keys=False
    ... )
    >>> print(text)
    ---
    date: 2023-05-12
    title: Sample
    tags:
        - test
        - sample
    nested:
        tags:
            - nested
    ---
    <BLANKLINE>
    # Title 1
    >>> reloaded = frontmatter.loads(text)
    >>> reloaded.metadata == post.metadata and reloaded.content == post.content
    True

``YAMLHandler`` uses block style by default. ``sort_keys=False`` keeps the
metadata's current key order. The same options can be passed to
:py:func:`frontmatter.dump` when writing a file, or to ``YAMLHandler.export``
when exporting metadata alone.

This chooses a new output format; it does not preserve the source's exact
formatting, comments or quoting.
