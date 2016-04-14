"""
Handlers for various kinds of metadata, including YAML, JSON and TOML
"""
from __future__ import unicode_literals

import json
import re
import yaml

try:
    import toml
except ImportError:
    toml = None


class BaseHandler(object):
    FM_BOUNDARY = None

    def __init__(self, fm_boundary=None):
        self.FM_BOUNDARY = fm_boundary or self.FM_BOUNDARY

        if self.FM_BOUNDARY is None:
            raise NotImplementedError('No frontmatter boundary defined. '
                'Please set {}.FM_BOUNDARY to a regular expression'.format(self.__class__.__name__))

    def load(self, fm):
        """
        Parse frontmatter and return a dict
        """
        raise NotImplementedError

    def split(self, text):
        """
        Split text into frontmatter and content
        """
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return fm, content


class YAMLHandler(BaseHandler):
    FM_BOUNDARY = re.compile(r'^-{3,}$', re.MULTILINE)

    def load(self, fm):
        return yaml.safe_load(fm)



class JSONHandler(BaseHandler):
    FM_BOUNDARY = re.compile(r'^(?:{|})$', re.MULTILINE)

    def load(self, fm):
        return json.loads(fm)

    def split(self, text):
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return "{" + fm + "}", content


if toml:
    class TOMLHandler(BaseHandler):
        FM_BOUNDARY = re.compile(r'^\+{3,}$', re.MULTILINE)

        def load(self, fm):
            return toml.loads(fm)

else:
    TOMLHandler = None