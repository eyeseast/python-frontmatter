#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as f:
    readme = f.read()


requirements = [
    'PyYAML',
    'six'
]


VERSION = '0.4.1'


setup(
    name = 'python-frontmatter',
    version = VERSION,
    description = 'Parse and manage posts with YAML frontmatter',
    long_description = readme,
    author = 'Chris Amico',
    author_email = 'eyeseast@gmail.com',
    url = 'https://github.com/eyeseast/python-frontmatter',
    packages = ['frontmatter'],
    include_package_data = True,
    install_requires = requirements,
    license = 'MIT',
    zip_safe = False,
    keywords = 'frontmatter',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='test',
)
