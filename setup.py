"""Setup file for the package, aliases:

.. code:: bash

    $ python setup.py lint
"""
import codecs
import distutils.cmd
import distutils.log
import os
import re
import subprocess
import sys

from pathlib import Path
from typing import List

from setuptools import find_packages, setup


# Pylint configuration
PYLINTRC_FILE = "pylintrc"
PYLINT_MINIMUM_SCORE = "9.0"
IGNORE_FOLDER = "test"

##############
# CORE PACKAGE
##############

NAME = "camelup"
PACKAGES = find_packages()
META_PATH = os.path.join("camelup", "__init__.py")
KEYWORDS = [""]
AUTHOR = "Michael Gracie"

PROJECT_URLS = {
    "Documentation": "https://github.com/pages/michael-gracie/camelup/build/html/index.html",
    "Bug Tracker": "https://github.com/michael-gracie/pages/camelup/issues",
    "Source Code": "https://github.com/michael-gracie/pages/camelup",
}

CLASSIFIERS = [
    "Intended Audience :: Everyone",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
]

INSTALL_REQUIRES = []
# if empty install for requirement.txt

if not INSTALL_REQUIRES:
    with open("requirements.txt", "r") as f:
        INSTALL_REQUIRES = f.read().split("\n")

EXTRAS_REQUIRE = {
    "docs": ["sphinx", "sphinx_rtd_theme"],
    "test": ["coverage", "pytest", "pytest-cov", "pytest-pylint"],
    "qa": ["pylint", "pre-commit", "black", "isort"],
}

EXTRAS_REQUIRE["dev"] = (
    EXTRAS_REQUIRE["test"] + EXTRAS_REQUIRE["docs"] + EXTRAS_REQUIRE["qa"]
)

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.rst"), encoding="utf-8") as file_open:
    LONG_DESCRIPTION = file_open.read()

with open(os.path.join(HERE, "LICENSE"), encoding="utf-8") as file_open:
    LICENSE = file_open.read()

############
# Installing
############


def version_check():
    if sys.version_info < (3, 7):
        sys.exit("Python 3.7 required.")


def install_pkg():
    """Setup for the package"""

    setup(
        name=NAME,
        description=LONG_DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        version="0.1.0",
        url="https://github.com/michael-gracie/camelup",
        project_urls=PROJECT_URLS,
        author=AUTHOR,
        license=LICENSE,
        python_requires="~=3.7.0",
        packages=PACKAGES,
        install_requires=INSTALL_REQUIRES,
        classifiers=CLASSIFIERS,
        extras_require=EXTRAS_REQUIRE,
        include_package_data=True,
        zip_safe=False,
        scripts=["bin/camelup"],
    )


if __name__ == "__main__":
    version_check()
    install_pkg()
