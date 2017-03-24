#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: vuolter
#      ____________
#   _ /       |    \ ___________ _ _______________ _ ___ _______________
#  /  |    ___/    |   _ __ _  _| |   ___  __ _ __| |   \\    ___  ___ _\
# /   \___/  ______/  | '_ \ || | |__/ _ \/ _` / _` |    \\  / _ \/ _ `/ \
# \       |   o|      | .__/\_, |____\___/\__,_\__,_|    // /_//_/\_, /  /
#  \______\    /______|_|___|__/________________________//______ /___/__/
#          \  /
#           \/

# import io
import os
import shutil
import subprocess

# from itertools import chain

from setuptools import Command, distutils, setup
from setuptools.command.sdist import sdist


class Compile(Command):
    """
    Compile the web user interface
    """
    description = 'compile the web user interface'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            # if os.name == 'nt':
                # # : Required by npm package `grunt-contrib-compress` under Windows
                # subprocess.check_call(
                    # 'npm install --global windows-build-tools', shell=True)
            subprocess.check_call(
                'cd pyload/webui && npm install --only=dev', shell=True)
            subprocess.check_call(
                'cd pyload/webui && node node_modules/grunt-cli/bin/grunt build',
                shell=True)
        except subprocess.CalledProcessError:
            distutils.log.warn("Failed to compile webui")
        shutil.rmtree('pyload/webui/node_modules', ignore_errors=True)
        return subprocess.call(
            'cd pyload/webui && npm install --production', shell=True)


class Configure(Command):
    """
    Configure the package
    """
    description = 'configure the package'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('compile')
        try:
            os.mkdir('locale')
        except OSError:
            pass
        self.run_command('extract_messages')
        self.run_command('init_catalog')
        # self.run_command('get_catalog')
        self.run_command('compile_catalog')


class GetCatalog(Command):
    """
    Download the translation catalog from the remote repository
    """
    description = 'download the translation catalog from the remote repository'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        raise NotImplementedError


class Sdist(sdist):
    """
    Custom ``sdist`` command
    """
    def run(self):
        self.run_command('configure')
        sdist.run(self)


NAME = "pyload.webui"
VERSION = "1.0.0"
STATUS = "1 - Planning"
DESC = """pyLoad WebUI module"""
LONG_DESC=io.open("README.md").read()
KEYWORDS = ["pyload"]
URL = "https://pyload.net"
DOWNLOAD_URL = "https://github.com/pyload/webui/releases"
LICENSE = "AGPLv3"
AUTHOR = "Walter Purcaro"
AUTHOR_EMAIL = "vuolter@gmail.com"
PLATFORMS = ['any']
PACKAGES = ['pyload', 'pyload/webui']
INCLUDE_PACKAGE_DATA = True
NAMESPACE_PACKAGES = ['pyload']
INSTALL_REQUIRES = [
    'Beaker>=1.6', 'Js2Py', 'bjoern;os_name!="nt"', 'bottle>=0.10', 'future',
    'pycryptodome', 'pyload.utils'
]
SETUP_REQUIRES = ['Babel', 'readme_renderer', 'recommonmark']
# TEST_SUITE = ''
# TESTS_REQUIRE = []
# EXTRAS_REQUIRE = {}
# EXTRAS_REQUIRE['full'] = list(set(chain(*EXTRAS_REQUIRE.values())))
PYTHON_REQUIRES = ">=2.6,!=3.0,!=3.1,!=3.2"
CMDCLASS = {
    'compile': Compile,
    'configure': Configure,
    'get_catalog': GetCatalog,
    'sdist': Sdist
}
MESSAGE_EXTRACTORS = {
    'pyload': [
        ('**.py', 'python', None),
        ('webui/app/scripts/**.js', 'javascript', None)
    ]
}
ZIP_SAFE = False
CLASSIFIERS = [
    "Development Status :: {0}".format(STATUS),
    "Environment :: Web Environment",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: {0}".format(LICENSE),
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Communications",
    "Topic :: Communications :: File Sharing",
    "Topic :: Internet",
    "Topic :: Internet :: File Transfer Protocol (FTP)",
    "Topic :: Internet :: WWW/HTTP"
]
SETUP_MAP = dict(
    name=NAME,
    version=VERSION,
    description=DESC,
    long_description=LONG_DESC,
    keywords=KEYWORDS,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    platforms=PLATFORMS,
    packages=PACKAGES,
    include_package_data=INCLUDE_PACKAGE_DATA,
    namespace_packages=NAMESPACE_PACKAGES,
    install_requires=INSTALL_REQUIRES,
    setup_requires=SETUP_REQUIRES,
    python_requires=PYTHON_REQUIRES,
    cmdclass=CMDCLASS,
    message_extractors=MESSAGE_EXTRACTORS,
    # test_suite=TEST_SUITE,
    # tests_require=TESTS_REQUIRE,
    zip_safe=ZIP_SAFE,
    classifiers=CLASSIFIERS
)

setup(**SETUP_MAP)
