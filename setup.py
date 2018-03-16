#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'six',
    'msgpack'
]
tests_require = install_requires + [
    "pytest",
]

setup(
    name='hippiepug',
    version=1.0,
    description='Merkle trees and hash chains with a flexible storage backend.',
    author='Bogdan Kulynych',
    author_email='hello@bogdankulynych.me',
    packages=['hippiepug'],
    license="MIT",
    install_requires=install_requires,
    tests_require=tests_require,
    extras={
        'test': tests_require
    }
)
