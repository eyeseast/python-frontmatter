#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function

import codecs
import doctest
import glob
import json
import sys
import unittest

import six

import frontmatter

try:
    import pyaml
except ImportError:
    pyaml = None


class FrontmatterTest(unittest.TestCase):
    """
    Tests for parsing various kinds of content and metadata
    """
    maxDiff = None

    def test_all_the_tests(self):
        "Sanity check that everything in the tests folder loads without errors"
        for filename in glob.glob('tests/*'):
            frontmatter.load(filename)

    def test_with_markdown_content(self):
        "Parse frontmatter and only the frontmatter"
        post = frontmatter.load('tests/hello-markdown.markdown')

        metadata = {'author': 'bob', 'something': 'else', 'test': 'tester'}
        for k, v in metadata.items():
            self.assertEqual(post[k], v)

    def test_unicode_post(self):
        "Ensure unicode is parsed correctly"
        chinese = frontmatter.load('tests/chinese.txt')

        self.assertTrue(isinstance(chinese.content, six.text_type))

        # this shouldn't work as ascii, because it's Hanzi
        self.assertRaises(UnicodeEncodeError, chinese.content.encode, 'ascii')

    def test_no_frontmatter(self):
        "This is not a zen exercise."
        post = frontmatter.load('tests/no-frontmatter.txt')
        with codecs.open('tests/no-frontmatter.txt', 'r', 'utf-8') as f:
            content = f.read().strip()

        self.assertEqual(post.metadata, {})
        self.assertEqual(post.content, content)

    def test_empty_frontmatter(self):
        "Frontmatter, but no metadata"
        post = frontmatter.load('tests/empty-frontmatter.txt')
        content = six.text_type("I have frontmatter but no metadata.")

        self.assertEqual(post.metadata, {})
        self.assertEqual(post.content, content)

    def test_to_dict(self):
        "Dump a post as a dict, for serializing"
        post = frontmatter.load('tests/network-diagrams.markdown')
        post_dict = post.to_dict()

        for k, v in post.metadata.items():
            self.assertEqual(post_dict[k], v)

        self.assertEqual(post_dict['content'], post.content)

    def test_to_string(self):
        "Calling str(post) returns post.content"
        post = frontmatter.load('tests/hello-world.markdown')

        # test unicode and bytes
        text = "Well, hello there, world."
        self.assertEqual(six.text_type(post), text)
        self.assertEqual(six.binary_type(post), text.encode('utf-8'))

    def test_pretty_dumping(self):
        "Use pyaml to dump nicer"
        # pyaml only runs on 2.7 and above
        if sys.version_info > (2, 6) and pyaml is not None:

            with codecs.open('tests/unpretty.md', 'r', 'utf-8') as f:
                data = f.read()

            post = frontmatter.load('tests/unpretty.md')
            yaml = pyaml.dump(post.metadata)

            # the unsafe dumper gives you nicer output, for times you want that
            dump = frontmatter.dumps(post, Dumper=pyaml.UnsafePrettyYAMLDumper)

            self.assertEqual(dump, data)
            self.assertTrue(yaml in dump)


if __name__ == "__main__":
    doctest.testfile('README.md')
    unittest.main()