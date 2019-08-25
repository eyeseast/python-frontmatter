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

.. autoclass:: frontmatter.default_handlers.BaseHandler
    :members: 

.. autoclass:: frontmatter.default_handlers.YAMLHandler

.. autoclass:: frontmatter.default_handlers.JSONHandler

.. autoclass:: frontmatter.default_handlers.TOMLHandler
