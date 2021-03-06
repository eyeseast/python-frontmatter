#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("README.md") as f:
    readme = f.read()


VERSION = "0.5.0"


setup(
    name="python-frontmatter",
    version=VERSION,
    description="Parse and manage posts with YAML (or other) frontmatter",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Chris Amico",
    author_email="eyeseast@gmail.com",
    url="https://github.com/eyeseast/python-frontmatter",
    packages=["frontmatter"],
    include_package_data=True,
    install_requires=["PyYAML"],
    extras_require={"test": ["pytest", "toml"]},
    tests_require=["python-frontmatter[test]"],
    license="MIT",
    zip_safe=False,
    keywords="frontmatter",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    test_suite="test",
)
