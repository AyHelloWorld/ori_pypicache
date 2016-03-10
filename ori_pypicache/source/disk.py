"""Stores packages on disk

"""
import os
import re


class FileNotInDisk(Exception):
    """Raised when a given package or file isn't found

    Aims to encapsulate packages not present locally or remotely.

    """


class NotOverwritingError(Exception):
    """Raised when attempting to overwrite an existing file

    """


class DiskPackageStore(object):
    def __init__(self, disk_path):
        self.disk_path = disk_path
        if not os.path.isdir(self.disk_path):
            os.mkdir(self.disk_path)

    def list_simple_info(self):
        """list cached packages in disk, ignore the package without '-'
        :return: sorted list

        """
        packages_set = set()
        for root, dirs, files in os.walk(self.disk_path):
            for filename in files:
                try:
                    package_name = filename[0:filename.index('-')]
                    packages_set.add(package_name.lower())
                except ValueError:
                    continue
        return sorted(list(packages_set))

    def list_package_info(self, package):
        """list cached versions of package in disk
        :return: sorted list
        """
        versions = list()
        for root, dirs, files in os.walk(self.disk_path):
            for filename in files:
                if filename.find('-') == -1:
                    continue

                def normalize(package_name):
                    return package_name.lower().replace('-', '_')

                my_package = filename[0:filename.index('-')]
                if normalize(package) == normalize(my_package):
                    versions.append(filename)
        return sorted(versions)

    def get_file(self, version):
        path = os.path.join(self.disk_path, version)
        try:
            return open(path, "rb")
        except IOError:
            raise FileNotInDisk(
                "Package version {0} not found in {1}".format(version, path))

    def add_file(self, version, content):
        path = os.path.join(self.disk_path, version)
        if os.path.isfile(path):
            if not re.search(
                    r'-(dev|SNAPSHOT)\.(zip|tar.gz|tar.bz2)$', version):
                raise NotOverwritingError(
                    "Not overwriting {0}".format(path))
        with open(path, "wb") as output:
            if hasattr(content, "read"):
                content = content.read()
            output.write(content)
