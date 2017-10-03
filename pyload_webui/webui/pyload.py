# -*- coding: utf-8 -*-
# @author: RaNaN

from __future__ import absolute_import, unicode_literals

import json
import os
import time

from future import standard_library

from bottle import redirect, request, response, route, static_file, template

from .iface import API, APPDIR, PREFIX, SETUP, UNAVAILABLE
from .utils import add_json_header, login_required, select_language

standard_library.install_aliases()

# Cache file names that are available gzipped
GZIPPED = {}


@route('/icons/<path:filename>')
def serve_icon(filename):
    # TODO: send real file, no redirects
    return redirect(PREFIX if PREFIX else '../images/icon.png')
    # return static_file(filename, root=join('tmp', 'icons'))


@route("/download/:fid")
@login_required('Download')
def download(fid, api):
    # TODO: check owner ship
    root, filename = api.get_file_path(fid)
    return static_file(filename, root, download=True)


@route("/i18n")
@route("/i18n/:lang")
def i18n(lang=None):
    add_json_header(response)
    if lang is None:
        pass
        # TODO: use lang from API.config or setup
    else:
        # TODO: auto choose language
        lang = select_language(("en",))
    return json.dumps({})


@route('/')
def index():
    # the browser should not set this, but remove in case to to avoid cached
    # requests
    if 'HTTP_IF_MODIFIED_SINCE' in request.environ:
        del request.environ['HTTP_IF_MODIFIED_SINCE']

    if UNAVAILABLE:
        return serve_static("unavailable.html")

    resp = serve_static('index.html')
    # set variable depending on setup mode
    setup = 'false' if SETUP is None else 'true'
    ws = API.get_ws_address() if API else False
    external = API.get_config_value('webui', 'external') if API else None
    web = None
    if API:
        web = API.get_config_value('webui', 'port')
    elif SETUP:
        web = SETUP.config.get('webui', 'port')

    # Render variables into the html page
    if resp.status_code == 200:
        content = resp.body.read()
        resp.body = template(content, ws=ws, web=web,
                             setup=setup, external=external, prefix=PREFIX)
        resp.content_length = len(resp.body) + 1

    # these page should not be cached at all
    resp.headers.append("Cache-Control", "no-cache")
    # they are rendered and last modified would be wrong
    if "Last-Modified" in resp.headers:
        del resp.headers['Last-Modified']

    return resp

# Very last route that is registered, could match all uris


@route('/<path:filename>')
def serve_static(filename):
    # save if this resource is available as gz
    if filename not in GZIPPED:
        GZIPPED[filename] = os.path.isfile(
            os.path.join(APPDIR, filename + ".gz"))

    # gzipped and clients accepts it
    # TODO: index.html is not gzipped, because of template processing
    gzipped = False
    if GZIPPED[filename] and "gzip" in request.get_header(
            "Accept-Encoding", "") and filename != "index.html":
        gzipped = True
        filename += ".gz"

    resp = static_file(filename, root=APPDIR)

    if filename.endswith(".html") or filename.endswith(".html.gz"):
        # tell the browser all html files must be revalidated
        resp.headers['Cache-Control'] = "must-revalidate"
    elif resp.status_code == 200:
        # expires after 7 days
        resp.headers['Expires'] = time.strftime(
            "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(
                time.time() + 60 * 60 * 24 * 7))
        resp.headers['Cache-control'] = "public"

    if gzipped:
        resp.headers['Vary'] = 'Accept-Encoding'
        resp.headers['Content-Encoding'] = 'gzip'

    return resp
