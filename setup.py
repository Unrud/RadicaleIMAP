#!/usr/bin/env python3

from setuptools import setup

VERSION = "2.0.0"

setup(
    name="Radicale_IMAP",
    version=VERSION,
    description="IMAP authentication plugin for Radicale",
    author="Unrud",
    author_email="unrud@outlook.com",
    url="http://github.com/Unrud/RadicaleIMAP",
    license="GNU GPL v3",
    platforms="Any",
    packages=["radicale_imap"],
    install_requires=["radicale>=2.0.0"])
