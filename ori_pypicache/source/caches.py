from urlparse import urlparse
import urllib
import pickle
import os

import cache
from cache import PyPIServerDisconnected, RemoteResponseNotOK


class RecordedServerNotFound(Exception):
    """Raised when server record of related package not found

    """


class PyPICaches(object):
    def __init__(self, disk_root, record_file_name, simple_renderer, versions_renderer):
        self.caches = dict()
        self.disk_root = disk_root
        self.record_file = os.path.join(disk_root, record_file_name)
        self.simple_renderer = simple_renderer
        self.versions_renderer = versions_renderer
        self.record_file_hdl = None

        for url in set(self._get_all_recorded_urls()):
            self.create_cache(server_simple_url=url)

    def create_cache(self, server_simple_url):
        new_cache_name = urlparse(server_simple_url).netloc
        if new_cache_name not in self.caches:
            store_path = os.path.join(self.disk_root,
                                      urllib.quote(new_cache_name))
            new_cache = cache.PyPICache(server_simple_url=server_simple_url,
                                        store_path=store_path)
            self.caches[new_cache_name] = new_cache

    def cache_exists(self, cache_name):
        if cache_name in self.caches:
            return True
        return False

    def get_simple_info(self):
        """list cached packages from all caches
        :return: sorted list

        """
        packages = list()
        for cache_name in self.caches:
            packages += self.caches[cache_name].list_simple_info()
        return self.simple_renderer(
            packages=sorted(packages, key=lambda d: d["name"]))

    def get_package_info(self, cache_name, package):
        """get info of package from pypi_server,
        record dict(package, pypi_server_simple_url),
        create new cache

        :return: HTML code

        """
        try:
            resp_content, pypi_server_simple_url = \
                self.caches[cache_name].get_package_info(package)
        except PyPIServerDisconnected:
            raise PyPIServerDisconnected
        self._record_package_where(package, pypi_server_simple_url)
        self.create_cache(server_simple_url=pypi_server_simple_url)
        return resp_content

    def get_package_info_from_recorded_server(self, package):
        try:
            cache_name = urlparse(self._get_package_where(package)).netloc
        except RecordedServerNotFound:
            raise RecordedServerNotFound

        try:
            return self.get_package_info(cache_name, package)
        except PyPIServerDisconnected:
            return self._get_cached_package_info(cache_name, package)

    def _get_cached_package_info(self, cache_name, package):
        assert cache_name in self.caches
        return self.versions_renderer(
            package=package,
            files=self.caches[cache_name].list_cached_package_info(package))
    
    def get_file(self, cache_name, version, file_path):
        assert cache_name in self.caches
        try:
            return self.caches[cache_name].get_file(version, file_path)
        except RemoteResponseNotOK:
            raise RemoteResponseNotOK

    def _record_package_where(self, package, pypi_server_url):
        records = self._read_records()
        records[package] = pypi_server_url
        self._write_records(records)

    def _get_package_where(self, package):
        records = self._read_records()
        try:
            return records[package]
        except KeyError:
            raise RecordedServerNotFound

    def _get_all_recorded_urls(self):
        return self._read_records().values()

    def _read_records(self):
        if os.path.isfile(self.record_file):
            with open(self.record_file, 'r') as f:
                res = pickle.load(f)
        else:
            res = {}

        self._protect_record_file()
        return res

    def _write_records(self, records):
        with open(self.record_file, 'w') as f:
            pickle.dump(records, f)

        self._protect_record_file()

    def _protect_record_file(self):
        try:
            self.record_file_hdl = open(self.record_file, 'r')
        except IOError:
            pass