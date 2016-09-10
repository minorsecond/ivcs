"""
Utilities for parsing files, creating hashes, etc.
"""

import os
import sys
import datetime
import hashlib
from PyQt4.QtCore import QThread, SIGNAL, QUrl, pyqtSignal, QObject
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
import platform
from ivcs import CheckoutStatusWindow


if platform.system == "Windows":
    # These are for creating hidden files
    import win32api, win32con, os


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

    def run(self):
        """
        Gets last modified time for file
        :param file: file to check
        :return: a datetime object
        """

        self.file_modified_time = os.path.getmtime(self.file)
        self.file_modified_time = datetime.datetime.fromtimestamp(self.file_modified_time)

        return self.file_modified_time


class FileCopier(QObject):
    """
    Copies files from network
    """

    finished = pyqtSignal()

    def __init__(self, file):
        super(FileCopier, self).__init__()
        self.file = QUrl("file:///{}".format(file))
        self.manager = QNetworkAccessManager(self)
        self.connect(self.manager, SIGNAL("finished(QNetworkReply*)"), self.reply_finished)

    def reply_finished(self, reply):
        checkout_class = CheckoutStatusWindow()
        self.connect(reply, SIGNAL("downloadProgress(int, int)"), checkout_class.update_progress_bar)
        self.reply = reply
        checkout_class.progressBar.setMaximum(reply.size())

    def run(self):
        """
        Start the download
        :return: None
        """
        self.manager.get(QNetworkRequest(self.file))
        self.finished.emit()


class GeneralFunctions:
    """
    Functions that don't need to be threaded
    """

    def __init__(self):
        self.file = None

    def hide_file(self, file):
        """
        Hides files in windows
        :return:
        """
        self.file = file
        if platform.system == "Windows":
            win32api.SetFileAttributes(self.file, win32con.FILE_ATTRIBUTE_HIDDEN)

    def get_application_path(self):
        """
        Gets the location of the executable file for storing data
        :return: None
        """

        application_path = None

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)

        elif __file__:
            application_path = os.path.join(os.path.dirname(__file__), '..')

        return application_path
