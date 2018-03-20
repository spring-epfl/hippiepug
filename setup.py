#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'six>=1.11.0',
    'msgpack>=0.5.6'
]

setup(
    name='hippiepug',
    version=0.1,
    description='Merkle trees and hash chains with a flexible storage backend.',
    author='Bogdan Kulynych',
    author_email='hello@bogdankulynych.me',
    packages=['hippiepug'],
    license="MIT",
    install_requires=install_requires
)
