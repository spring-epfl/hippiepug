#!/usr/bin/env python
import os

from setuptools import setup
from hippiepug.meta import __author__, __version__, description

install_requires = [
    'six>=1.11.0',
    'msgpack>=0.5.6',
    'attrs>=17.4.0'
]
setup_requires = [
    'pytest-runner',
]


test_requires = [
    'pytest',
    'mock',
    'pytest-lazy-fixture'
]
dev_requires = test_requires + [
    'sphinx',
    'sphinx_rtd_theme'
]


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
        long_description = f.read()


setup(
    name='hippiepug',
    version=__version__,
    description=description,
    long_description=long_description,
    author=__author__,
    author_email='hello@bogdankulynych.me',
    packages=['hippiepug'],
    license="AGPL",
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=test_requires,
    extras_require={
        'dev': dev_requires
    }
)
