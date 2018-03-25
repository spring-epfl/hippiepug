#!/usr/bin/env python
import os
import re

from setuptools import setup


INSTALL_REQUIRES = [
    'attrs>=17.4.0',
    'msgpack>=0.5.6',
    'defaultcontext>=1.1.0',
]

SETUP_REQUIRES = [
    'pytest-runner',
]

TEST_REQUIRES = [
    'pytest',
    'mock',
    'pytest-lazy-fixture',
]

DEV_REQUIRES = TEST_REQUIRES + [
    'sphinx',
    'sphinx_rtd_theme'
]


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
        long_description = f.read()


with open(os.path.join(here, 'hippiepug/__init__.py')) as f:
    matches = re.findall(r'(__.+__) = \'(.*)\'', f.read())
    for var_name, var_value in matches:
        globals()[var_name] = var_value


setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=long_description,
    author=__author__,
    author_email=__email__,
    packages=['hippiepug'],
    license=__license__,
    install_requires=INSTALL_REQUIRES,
    setup_requires=SETUP_REQUIRES,
    tests_require=TEST_REQUIRES,
    extras_require={
        'dev': DEV_REQUIRES,
        'test': TEST_REQUIRES
    }
)
