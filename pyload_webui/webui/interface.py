#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: RaNaN

from __future__ import absolute_import, unicode_literals

import os
import sys

from future import standard_library
from pkg_resources import resource_exists, resource_filename

import bottle
from pyload.core.thread import webserver as ServerThread  # TODO: Recheck...
# Last routes to register
from pyload.webui import api, cnl, pyload, setup

from .__about__ import __package__
from .middlewares import (PrefixMiddleware, SessionMiddleware,
                          StripPathMiddleware)

standard_library.install_aliases()

SETUP = None
API = None

if not ServerThread.core:
    if ServerThread.setup:
        SETUP = ServerThread.setup
        config = SETUP.config
    else:
        raise Exception("Could not access pyLoad Core")
else:
    API = ServerThread.core.api
    config = ServerThread.core.config

TEMPLATE = "default"
DL_ROOT = config.get('general', 'storage_folder')
PREFIX = config.get('webui', 'prefix')

if PREFIX:
    PREFIX = PREFIX.rstrip("/")
    if PREFIX and not PREFIX.startswith("/"):
        PREFIX = "/{0}".format(PREFIX)

# webui build is available
if resource_exists(__package__, 'node_modules'):
    UNAVAILABLE = False
else:
    UNAVAILABLE = True

if resource_exists(__package__, 'min/index.html'):
    APPDIR = resource_filename(__package__, 'min')
else:
    APPDIR = resource_filename(__package__, 'app')

DEBUG = config.get(
    'webui', 'debug') or "-d" in sys.argv or "--debug" in sys.argv
bottle.debug(DEBUG)

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': False,
    'session.data_dir': './tmp',
    'session.auto': False
}

session = SessionMiddleware(bottle.app(), session_opts)
web = StripPathMiddleware(session)

if PREFIX:
    web = PrefixMiddleware(web, prefix=PREFIX)

# Server Adapter


def run_server(host, port, server):
    bottle.run(app=web, host=host, port=port, quiet=True, server=server)


if __name__ == '__main__':
    bottle.run(app=web, port=8010)
