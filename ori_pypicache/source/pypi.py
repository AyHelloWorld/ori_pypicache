"""Handles requests to the real PyPI package index

"""
from HTMLParser import HTMLParser
from urlparse import urlparse
import datetime
import requests
import logging
import os

try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib


class RemoteResponseNotOK(Exception):
    """Raised when unexpected response from requesting a uri

    """


class PyPIServerDisconnected(Exception):
    """Raised when url cannot be connected

    """


def get_uri(uri):
    """Request the given URI and return the response
    and redirected uri if existed

    Check response and raise RemoteServerNotOK if error

    """
    headers = {'User-Agent': 'pip/7.1.0'}
    response = requests.get(uri, headers=headers)
    if response.status_code != 200:
        raise RemoteResponseNotOK(
            "Unexpected response from {0}".format(uri), response)

    redirect_uri = None
    if response.history:
        redirect_uri = response.url
    return response, redirect_uri


def timestamp():
    return datetime.datetime.now()


def convert_links(resp_content, uri):
    class MyHTMLParser(HTMLParser):
        def __init__(self):
            self.links = list()
            HTMLParser.__init__(self)

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for name, value in attrs:
                    if name == 'href':
                        self.links.append(value)

    url_parse = urlparse(uri)
    parser = MyHTMLParser()
    parser.feed(resp_content)
    for ele in parser.links:
        if ele.startswith('/'):
            new_ele = "/{0}{1}".format(url_parse.netloc, ele)
        else:
            new_ele = os.path.normpath(
                "/{0}{1}/{2}".format(url_parse.netloc, url_parse.path, ele))
            new_ele = new_ele.replace('\\', '/')
        resp_content = resp_content.replace(ele, new_ele)
    return resp_content


class PyPI(object):
    """Handles requests to the real PyPI servers
    http://ni-pypi.amer.corp.natinst.com/simple/
    http://ni-pypi.amer.corp.natinst.com:3141/root/pypi/+simple/

    """
    def __init__(self, server_simple):
        if not server_simple.endswith('/'):
            server_simple += '/'

        self.server_simple = server_simple
        self.last_try_time = None

        logging.info("Create {0} last_try_time {1}".format(
            self.server_simple, self.last_try_time))

    def get_package_info(self, package):
        """get all versions of package on server
        :return: response content, redirected uri

        """
        if self.last_try_time is not None:
            elapsed = timestamp() - self.last_try_time
            if elapsed <= datetime.timedelta(seconds=900):
                raise PyPIServerDisconnected

        uri = "{0}{1}".format(self.server_simple, package)
        try:
            response, redirect_uri = get_uri(uri)
        except requests.ConnectionError:
            self.last_try_time = timestamp()
            logging.info("Update {0}'s last_try_time {1}".format(
                self.server_simple, self.last_try_time))
            raise PyPIServerDisconnected

        if redirect_uri is not None:
            request_uri = os.path.dirname(redirect_uri)
        else:
            request_uri = uri
        resp_content = convert_links(response.content, request_uri)
        return resp_content, redirect_uri

    def get_file(self, filename, file_path):
        """
        :returns: package data

        """
        url_parse = urlparse(self.server_simple)
        uri = "{0}://{1}/{2}/{3}".format(
            url_parse.scheme, url_parse.netloc, file_path, filename)
        logging.info("==" + "get_file %s" % uri)
        response, url = get_uri(uri)
        return response.content
