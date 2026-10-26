API
====

.. module:: frontmatter

Reading
-------

.. autofunction:: frontmatter.parse

.. autofunction:: frontmatter.check

.. autofunction:: frontmatter.checks

.. autofunction:: frontmatter.load

.. autofunction:: frontmatter.loads


Writing
-------

.. autofunction:: frontmatter.dump

.. autofunction:: frontmatter.dumps


Post objects
------------

.. autoclass:: frontmatter.Post
    :members:
    :special-members: __getitem__, __setitem__, __delitem__


Handlers
--------

See :doc:`handlers` for the handler API and customization examples:

* :class:`~frontmatter.default_handlers.BaseHandler`
* :class:`~frontmatter.default_handlers.YAMLHandler`
* :class:`~frontmatter.default_handlers.JSONHandler`
* :class:`~frontmatter.default_handlers.TOMLHandler`
