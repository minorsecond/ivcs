"""
Utilities for parsing files, creating hashes, etc.
"""

import os
import datetime
import hashlib
from PyQt4.QtCore import QThread


class FileSystemWalker(QThread):
    """
    Traverses the FS and finds files
    """

    def __init__(self, path, image_extensions):
        super(FileSystemWalker, self).__init__()
        self.path = path
        self.image_extensions = image_extensions
        self.hash_chunksize = 4096

        self.files = []
        self.subdirs = []
        self.file_modified_time = None

    def __del__(self):
        self.wait()

    def run(self):
        """
        Walks paths and files, and returns sets of files and directories
        :return: sets of files and directories
        """

        for root, dirs, filenames in os.walk(self.path):
            for subdir in dirs:
                self.subdirs.append(os.path.join(root, subdir))

            for file in filenames:
                if os.path.splitext(file)[1] in self.image_extensions:
                    self.files.append(os.path.join(root, file))

        return self.files, self.subdirs


class FileHasher(QThread):
    """
    Contains the methods for hashing files and directories
    """

    def __init__(self, file):
        super(FileHasher, self).__init__()
        self.file = file
        self.hash_chunksize = 4096

    def __del__(self):
        self.wait()

    def run(self):
        """
        Generates SHA256 for file.
        :param file: file to check
        :return: an sha256 hex
        """

        sha = hashlib.sha256()

        with open(self.file, 'rb') as f:
            while True:
                data = f.read(self.hash_chunksize)
                if data:
                    sha.update(data)
                else:
                    break

        return sha.hexdigest()


class FileModifiedTimeGetter(QThread):
    """
    Contains the methods for hashing files and directories
    """

    def __init__(self, file):
        super(FileModifiedTimeGetter, self).__init__()
        self.file = file
        self.file_modified_time = None

        def __del__(self):
            self.wait()

    def run(self, file):
        """
        Gets last modified time for file
        :param file: file to check
        :return: a datetime object
        """

        self.file_modified_time = os.path.getmtime(file)
        self.file_modified_time = datetime.datetime.fromtimestamp(self.file_modified_time)

        return self.file_modified_time
