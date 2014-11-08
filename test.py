#!/usr/bin/env python
from __future__ import unicode_literals

import doctest
import unittest

import frontmatter


class FrontmatterTest(unittest.TestCase):
    """
    Tests for parsing various kinds of content and metadata
    """

    def test_unicode_post(self):
        "Ensure unicode is parsed correctly"
        chinese = frontmatter.load('tests/chinese.txt')

        self.assertTrue(isinstance(chinese.content, unicode))

        # this shouldn't work as ascii, because it's Hanzi
        self.assertRaises(UnicodeEncodeError, chinese.content.encode, 'ascii')


if __name__ == "__main__":
    doctest.testfile('README.md')
    unittest.main()