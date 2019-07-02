#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import codecs
import doctest
import glob
import json
import os
import shutil
import sys
import tempfile
import textwrap
import unittest

import six

import frontmatter
from frontmatter.default_handlers import YAMLHandler, JSONHandler, TOMLHandler

try:
    import pyaml
except ImportError:
    pyaml = None
try:
    import toml
except ImportError:
    toml = None


class FrontmatterTest(unittest.TestCase):
    """
    Tests for parsing various kinds of content and metadata
    """

    maxDiff = None

    def test_all_the_tests(self):
        "Sanity check that everything in the tests folder loads without errors"
        for filename in glob.glob("tests/*"):
            frontmatter.load(filename)

    def test_with_markdown_content(self):
        "Parse frontmatter and only the frontmatter"
        post = frontmatter.load("tests/hello-markdown.markdown")

        metadata = {"author": "bob", "something": "else", "test": "tester"}
        for k, v in metadata.items():
            self.assertEqual(post[k], v)

    def test_unicode_post(self):
        "Ensure unicode is parsed correctly"
        chinese = frontmatter.load("tests/chinese.txt", "utf-8")
        output = frontmatter.dumps(chinese)
        zh = "中文"

        self.assertTrue(isinstance(chinese.content, six.text_type))

        # check that we're dumping out unicode metadata, too
        self.assertTrue(zh in output)

        # this shouldn't work as ascii, because it's Hanzi
        self.assertRaises(UnicodeEncodeError, chinese.content.encode, "ascii")

    def test_no_frontmatter(self):
        "This is not a zen exercise."
        post = frontmatter.load("tests/no-frontmatter.txt")
        with codecs.open("tests/no-frontmatter.txt", "r", "utf-8") as f:
            content = f.read().strip()

        self.assertEqual(post.metadata, {})
        self.assertEqual(post.content, content)

    def test_empty_frontmatter(self):
        "Frontmatter, but no metadata"
        post = frontmatter.load("tests/empty-frontmatter.txt")
        content = six.text_type("I have frontmatter but no metadata.")

        self.assertEqual(post.metadata, {})
        self.assertEqual(post.content, content)

    def test_extra_space(self):
        "Extra space in frontmatter delimiter"
        post = frontmatter.load("tests/extra-space.txt")
        content = six.text_type(
            "This file has an extra space on the opening line of the frontmatter."
        )

        self.assertEqual(post.content, content)
        metadata = {"something": "else", "test": "tester"}
        for k, v in metadata.items():
            self.assertEqual(post[k], v)

    def test_to_dict(self):
        "Dump a post as a dict, for serializing"
        post = frontmatter.load("tests/network-diagrams.markdown")
        post_dict = post.to_dict()

        for k, v in post.metadata.items():
            self.assertEqual(post_dict[k], v)

        self.assertEqual(post_dict["content"], post.content)

    def test_to_string(self):
        "Calling str(post) returns post.content"
        post = frontmatter.load("tests/hello-world.markdown")

        # test unicode and bytes
        text = "Well, hello there, world."
        self.assertEqual(six.text_type(post), text)
        self.assertEqual(six.binary_type(post), text.encode("utf-8"))

    def test_pretty_dumping(self):
        "Use pyaml to dump nicer"
        # pyaml only runs on 2.7 and above
        if sys.version_info > (2, 6) and pyaml is not None:

            with codecs.open("tests/unpretty.md", "r", "utf-8") as f:
                data = f.read()

            post = frontmatter.load("tests/unpretty.md")
            yaml = pyaml.dump(post.metadata)

            # the unsafe dumper gives you nicer output, for times you want that
            dump = frontmatter.dumps(post, Dumper=pyaml.UnsafePrettyYAMLDumper)

            self.assertEqual(dump, data)
            self.assertTrue(yaml in dump)

    def test_with_crlf_string(self):
        import codecs

        markdown_bytes = b'---\r\ntitle: "my title"\r\ncontent_type: "post"\r\npublished: no\r\n---\r\n\r\nwrite your content in markdown here'
        loaded = frontmatter.loads(markdown_bytes, "utf-8")
        self.assertEqual(loaded["title"], "my title")

    def test_dumping_with_custom_delimiters(self):
        "dump with custom delimiters"
        post = frontmatter.load("tests/hello-world.markdown")
        dump = frontmatter.dumps(post, start_delimiter="+++", end_delimiter="+++")

        self.assertTrue("+++" in dump)

    def test_dump_to_file(self):
        "dump post to filename"
        post = frontmatter.load("tests/hello-world.markdown")

        tempdir = tempfile.mkdtemp()
        filename = os.path.join(tempdir, "hello.md")
        frontmatter.dump(post, filename)

        with open(filename) as f:
            self.assertEqual(f.read(), frontmatter.dumps(post))

        # cleanup
        shutil.rmtree(tempdir)


class HandlerTest(unittest.TestCase):
    """
    Tests for custom handlers and formatting
    """

    TEST_FILES = {
        "tests/hello-world.markdown": YAMLHandler,
        "tests/hello-json.markdown": JSONHandler,
        "tests/hello-toml.markdown": TOMLHandler,
    }

    def sanity_check(self, filename, handler_type):
        "Ensure we can load -> dump -> load"
        post = frontmatter.load(filename)

        self.assertIsInstance(post.handler, handler_type)

        # dump and reload
        repost = frontmatter.loads(frontmatter.dumps(post))

        self.assertEqual(post.metadata, repost.metadata)
        self.assertEqual(post.content, repost.content)
        self.assertEqual(post.handler, repost.handler)

    def test_detect_format(self):
        "detect format based on default handlers"

        for filename, Handler in self.TEST_FILES.items():
            with codecs.open(filename, "r", "utf-8") as f:
                format = frontmatter.detect_format(f.read(), frontmatter.handlers)
                self.assertIsInstance(format, Handler)

    def test_sanity_all(self):
        "Run sanity check on all handlers"
        for filename, Handler in self.TEST_FILES.items():
            self.sanity_check(filename, Handler)

    def test_no_handler(self):
        "default to YAMLHandler when no handler is attached"
        post = frontmatter.load("tests/hello-world.markdown")
        del post.handler

        text = frontmatter.dumps(post)
        self.assertIsInstance(
            frontmatter.detect_format(text, frontmatter.handlers), YAMLHandler
        )

    def test_custom_handler(self):
        "allow caller to specify a custom delimiter/handler"

        # not including this in the regular test directory
        # because it would/should be invalid per the defaults
        custom = textwrap.dedent(
            """
        ...
        dummy frontmatter
        ...
        dummy content
        """
        )

        # and a custom handler that really doesn't do anything
        class DummyHandler(object):
            def load(self, fm):
                return {"value": fm}

            def split(self, text):
                return "dummy frontmatter", "dummy content"

        # but we tell frontmatter that it is the appropriate handler
        # for the '...' delimiter
        # frontmatter.handlers['...'] = DummyHandler()
        post = frontmatter.loads(custom, handler=DummyHandler())

        self.assertEqual(post["value"], "dummy frontmatter")

    def test_toml(self):
        "load toml frontmatter"
        if toml is None:
            return
        post = frontmatter.load("tests/hello-toml.markdown")
        metadata = {"author": "bob", "something": "else", "test": "tester"}
        for k, v in metadata.items():
            self.assertEqual(post[k], v)

    def test_json(self):
        "load raw JSON frontmatter"
        post = frontmatter.load("tests/hello-json.markdown")
        metadata = {"author": "bob", "something": "else", "test": "tester"}
        for k, v in metadata.items():
            self.assertEqual(post[k], v)


class HandlerBaseTest:
    """
    Tests for frontmatter.handlers
    """

    def setUp(self):
        """
        This method should be overridden to initalize the TestCase
        """
        self.handler = None
        self.data = {
            "filename": "tests/hello-world.markdown",
            "content": """\
""",
            "metadata": {},
        }

    def read_from_tests(self):
        with open(self.data["filename"]) as fil:
            return fil.read()

    def test_external(self):
        filename = self.data["filename"]
        content = self.data["content"]
        metadata = self.data["metadata"]
        content_stripped = content.strip()

        post = frontmatter.load(filename)

        self.assertEqual(post.content, content_stripped)
        for k, v in metadata.items():
            self.assertEqual(post[k], v)

        # dumps and then loads to ensure round trip conversions.
        posttext = frontmatter.dumps(post, handler=self.handler)
        post_2 = frontmatter.loads(posttext)

        for k in post.metadata:
            self.assertEqual(post.metadata[k], post_2.metadata[k])

        self.assertEqual(post.content, post_2.content)

    def test_detect(self):
        text = self.read_from_tests()

        self.assertTrue(self.handler.detect(text))

    def test_split_content(self):
        text = self.read_from_tests()

        fm, content = self.handler.split(text)

        self.assertEqual(content, self.data["content"])

    def test_split_load(self):
        text = self.read_from_tests()
        fm, content = self.handler.split(text)
        fm_load = self.handler.load(fm)

        # The format of the failmsg makes it easy to copy into the test.
        any_fail = False
        failmsg = "The following metadata did not match the test:"
        for k in self.data["metadata"]:
            if fm_load[k] == self.data["metadata"][k]:
                continue
            any_fail = True
            failmsg += '\n"{0}": {1},'.format(k, repr(fm_load[k]))

        if any_fail:
            self.fail(failmsg)

    @unittest.skip("metadata can be reordered")
    def test_split_export(self):
        text = self.read_from_tests()
        fm, content = self.handler.split(text)

        fm_export = self.handler.export(self.data["metadata"])

        self.assertEqual(fm_export, fm)


class YAMLHandlerTest(HandlerBaseTest, unittest.TestCase):
    def setUp(self):
        self.handler = YAMLHandler()
        self.data = {
            "filename": "tests/hello-markdown.markdown",
            # TODO: YAMLHandler.split() is prepending '\n' to the content
            "content": """\

Title
=====

title2
------

Hello.

Just need three dashes
---

And this shouldn't break.""",
            "metadata": {"test": "tester", "author": "bob", "something": "else"},
        }


class JSONHandlerTest(HandlerBaseTest, unittest.TestCase):
    def setUp(self):
        self.handler = JSONHandler()
        self.data = {
            "filename": "tests/hello-json.markdown",
            # TODO: JSONHandler.split() is prepending '\n' to the content
            "content": """\


Title
=====

title2
------

Hello.

Just need three dashes
---

And this might break.
""",
            "metadata": {"test": "tester", "author": "bob", "something": "else"},
        }


class TOMLHandlerTest(HandlerBaseTest, unittest.TestCase):
    def setUp(self):
        self.handler = TOMLHandler()
        self.data = {
            "filename": "tests/hello-toml.markdown",
            # TODO: TOMLHandler.split() is prepending '\n' to the content
            "content": """\

Title
=====

title2
------

Hello.

Just need three dashes
---

And this shouldn't break.
""",
            "metadata": {"test": "tester", "author": "bob", "something": "else"},
        }


if __name__ == "__main__":
    doctest.testfile("README.md")
    doctest.testmod(
        frontmatter.default_handlers, extraglobs={"frontmatter": frontmatter}
    )
    unittest.main()
