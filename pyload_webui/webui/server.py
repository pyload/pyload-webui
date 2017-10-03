# -*- coding: utf-8 -*-
# @author: vuolter

from pyload.utils.layer.safethreading import Thread
























from __future__ import unicode_literals

import os
import threading

from pyload import webui
from pyload.utils import web


def auto(app, host, port, key=None, cert=None):
    bottle.run(app=app, host=host, port=port, server="auto", quiet=True,
               certfile=cert, keyfile=key)


def lightweight(app, host, port, key=None, cert=None):
    bottle.run(app=app, host=host, port=port, server="bjoern", quiet=True,
               reuse_port=True)


def threaded(app, host, port, key=None, cert=None):
    bottle.run(app=app, host=host, port=port, server="cherrypy", quiet=True,
               certfile=cert, keyfile=key)


def fastcgi(app, host, port, key=None, cert=None):
    bottle.run(app=app, host=host, port=port, server="flup", quiet=True,
               certfile=cert, keyfile=key)
               
               
class ServerThread(threading.Thread):

    def __init__(self, core,
                 server=None, host=None, port=None, key=None, cert=None, ssl=True):
        """
        Constructor
        """
        threading.Thread.__init__(self)
        self.setDaemon(True)

        # self.manager = manager  #: thread manager
        # self.pyload  = manager.pyload
        self.pyload    = core

        self.server = server or "auto"
        self.host   = host or "localhost"
        self.port   = port or 80
        self.key    = key or None
        self.cert   = cert or None
        self.ssl    = ssl or True


    def run(self):
        key  = None
        cert = None

        if os.name == 'nt' and self.server == "lightweight":
            self.pyload.log.info(_("Server set to `auto`"),
                                 _("Lightweight server not supported under Windows"))
            self.server = "auto"

        elif self.server not in dir(webui.servers):
            self.pyload.log.warning(_("Server set to `auto`"), e)
            self.server = "auto"

        if self.ssl:
            if not os.path.isfile(self.key) or not os.path.isfile(self.cert):
                self.pyload.log.warning(_("SSL key/cert file not found"))
                self.ssl = False
            elif self.server == 'lightweight':
                self.pyload.log.warning(_("SSL encryption disabled because not supported"))
                self.ssl = False
            else:
                self.log.info(_("SSL encryption enabled"))
                key  = self.key
                cert = self.cert

        try:
            self._run_server(self.server, self.host, self.port, key, cert)
        except ValueError:  #@NOTE: Workaround to issue `https://github.com/pyload/pyload/issues/1145`
            pass


    def _run_server(self, type, host, port, key, cert):
        self.pyload.log.info(_("Starting {} webserver: {}:{}").format(type, host, port))
        webserver = getattr(web.server, type)
        webserver(webui.app, host, port, key, cert)
