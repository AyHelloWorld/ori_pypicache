from urlparse import urlparse
import logging
import os

from pypi import PyPIServerDisconnected, RemoteResponseNotOK
import pypi
import disk


class PyPICache(object):
    """A proxying cache for python packages
    Reads from PyPI and writes to a local location
    Tries to mirror the PyPI structure

    """
    def __init__(self, server_simple_url, store_path):
        self.server_simple_url = server_simple_url
        self.pypi_server = pypi.PyPI(server_simple=server_simple_url)
        self.server_name = urlparse(server_simple_url).netloc
        self.pypi_store = disk.DiskPackageStore(disk_path=store_path)

    def list_simple_info(self):
        """format list of cached packages in disk
        :return: sorted list

        """
        packages_list = self.pypi_store.list_simple_info()
        formatted_packages_list = list()
        for package in packages_list:
            formatted_packages_list.append(
                dict(server=self.server_name, name=package))
        return sorted(formatted_packages_list, key=lambda d: d["name"])

    def get_package_info(self, package):
        """get info of package from pypi_server
        :return: HTML code, server_simple_url

        """
        try:
            resp_content, redirect_uri = \
                self.pypi_server.get_package_info(package)
        except PyPIServerDisconnected:
            raise PyPIServerDisconnected

        if redirect_uri:
            fallback_server = os.path.dirname(redirect_uri)
            return resp_content, fallback_server
            # http://ni-pypi.amer.corp.natinst.com:3141/root/pypi/+simple
        else:
            return resp_content, self.server_simple_url

    def list_cached_package_info(self, package):
        versions_list = self.pypi_store.list_package_info(package)
        formatted_versions_list = list()
        for version in versions_list:
            formatted_versions_list.append(
                dict(server=self.server_name, version=version))
        return sorted(formatted_versions_list, key=lambda d: d["version"])

    def get_file(self, filename, file_path):
        """Fetches a package file
        Attempts to use the local cache before falling back to PyPI.

        :returns: package file data
        - TODO: Change to returning a iterable

        """

        def get():
            return self.pypi_store.get_file(filename).read()

        try:
            return get()
        except disk.FileNotInDisk:
            logging.info("{0} not found in disk".format(filename))
            resp_content = self.pypi_server.get_file(filename, file_path)
            self.pypi_store.add_file(filename, resp_content)
            return get()
