#!/usr/bin/env python
import os

from setuptools import setup


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
    version=0.1,
    description=(
        'Sublinear-traversal blockchains and efficient key-value Merkle trees '
        'with a flexible storage backend.'),
    long_description=long_description,
    author='Bogdan Kulynych',
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
