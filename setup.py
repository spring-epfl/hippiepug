#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'six==1.11.0',
    'msgpack==0.5.6'
]
tests_require = install_requires + [
    "pytest==3.4.2",
]

setup(
    name='hippiepug',
    version=0.0,
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
