#!/usr/bin/env python
# -*- coding: latin-1 -*-
import codecs
import os
from setuptools import setup, find_packages
from vocexcel import __version__


def open_local(paths, mode="r", encoding="utf8"):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), *paths)
    return codecs.open(path, mode, encoding)


with open_local(["README.rst"], encoding="utf-8") as readme:
    long_description = readme.read()

# with open_local(["requirements.txt"]) as req:
#     install_requires = req.read().split("\n")
install_requires = [
    "openpyxl",
    "rdflib @ git+https://github.com/RDFlib/rdflib.git#egg=rdflib",
    "pydantic",
    "pyshacl",
    "dateutils",
]

setup(
    name="VocExcel",
    packages=find_packages(),
    package_dir={"vocexcel": "vocexcel"},
    package_data={
        "vocexcel": ["validator.vocpub.ttl", "blank.xlsx"],
    },
    include_package_data=True,
    version=__version__,
    description="Another Excel to RDF converter for SKOS vocabs, "
    "but one that include profile-based validation of results",
    author="Nicholas J. Car",
    author_email="nicholas.car@surroundaustralia.com",
    url="https://github.com/surroundaustralia/vocexcel",
    download_url="https://github.com/surroundaustralia/vocexcel/archive/v{:s}.tar.gz".format(
        __version__
    ),
    license="LICENSE",
    keywords=["SKOS", "vocabulary", "Excel", "converter", "validate", "profile"],
    long_description=long_description,
    entry_points={
        "console_scripts": [
            "vocexcel = vocexcel.convert:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Bug Reports": "https://github.com/surroundaustralia/vocexcel/issues",
        "Source": "https://github.com/surroundaustralia/vocexcel/",
    },
    install_requires=install_requires,
    long_description_content_type="text/x-rst",
)
