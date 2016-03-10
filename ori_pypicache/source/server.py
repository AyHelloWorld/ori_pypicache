"""pypicache server

"""
from flask import Flask, make_response, render_template, abort
from werkzeug.routing import BaseConverter
import werkzeug.exceptions as ex
from urlparse import urlparse
import mimetypes
import logging

import caches as caches_module


def create_renderer(template):
    def renderer(**args):
        return render_template(template, **args)
    return renderer


class GatewayTimeout(ex.HTTPException):
    code = 504
    description = 'The proxy server receive a timeout response ' \
                  'from the upstream server. \n ' \
                  'And the local has not record about it.'
abort.mapping.update({504: GatewayTimeout})


class RegexConverter(BaseConverter):
    def __init__(self, map, *args):
        super(RegexConverter, self).__init__(map)
        self.map = map
        self.regex = args[0]

app = Flask("ori_pypicache")
app.url_map.converters['regex'] = RegexConverter


def configure(upstream_server_url, disk_root, record_file_name):
    simple_renderer = create_renderer("simple.html")
    versions_renderer = create_renderer("simple_package.html")
    app.config["caches"] = caches_module.PyPICaches(
        disk_root, record_file_name, simple_renderer, versions_renderer)
    caches().create_cache(server_simple_url=upstream_server_url)
    app.config["upstream_server_name"] = urlparse(upstream_server_url).netloc
    return app


def caches():
    return app.config["caches"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/simple/")
def simple_index():
    return caches().get_simple_info()


@app.route("/simple/<package>/")
def simple_package_info(package):
    try:
        return caches().get_package_info(app.config["upstream_server_name"], 
                                         package)
    except caches_module.PyPIServerDisconnected:
        try:
            return caches().get_package_info_from_recorded_server(package)
        except caches_module.RecordedServerNotFound:
            return abort(504)


@app.route("/<pypi_server_name>/<regex(\".*\"):file_path>/<version>",
           methods=["GET"])
def get_file(pypi_server_name, file_path, version):
    logging.info(pypi_server_name + "==" + file_path + "==" + version)
    if not caches().cache_exists(pypi_server_name):
        return abort(404)
    try:
        response = make_response(
            caches().get_file(pypi_server_name, version, file_path))
    except caches_module.RemoteResponseNotOK:
        return abort(404)
    return _set_response_content_type(response, version)


def _set_response_content_type(response, filename):
    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None and filename.endswith(".egg"):
        content_type = "application/zip"
    logging.debug("Setting mime type of {0!r} to {1!r}".format(
        filename, content_type))
    response.content_type = content_type
    return response
