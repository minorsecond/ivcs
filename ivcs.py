"""
Imagery Version Control System
2016 Robert Ross Wardrup
"""

import os
import configparser
import sys
import shutil
import hashlib
import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from database import ImageryDatabase
from gui import commit_message_window, ivcs_mainwindow, settings_window, view_message_window
import compressor


class MainWindow(ivcs_mainwindow.QtGui.QMainWindow, ivcs_mainwindow.Ui_MainWindow):
    def __init__(self):
        ivcs_mainwindow.QtGui.QMainWindow.__init__(self)
        ivcs_mainwindow.Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # elf.setFixedHeight(self.size())

        self.image_extensions = []

        # Create config file
        app_dir = get_application_path()
        if not os.path.exists(os.path.join(app_dir, 'ivcs.ini')):

            # Disable all GUI elements until a branch is set and scanned
            self.RemoteFileList.setEnabled(False)
            self.LocalFileList.setEnabled(False)
            self.RemoteChangeList.setEnabled(False)
            self.LocalChangeList.setEnabled(False)

            self.CheckoutButton.setEnabled(False)
            self.ViewRemoteCommitButton.setEnabled(False)
            self.CommitButton.setEnabled(False)
            self.PushButton.setEnabled(False)


class SettingsWindow(settings_window.QtGui.QDialog, settings_window.Ui_Dialog):
    """
    Settings Window
    """

    def __init__(self):
        settings_window.QtGui.QDialog.__init__(self)
        settings_window.Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.image_extensions = []

        if self.ImgExtensionCheckBox.isChecked():
            self.image_extensions.append('.img')

        if self.TifExtensionCheckBox.isChecked():
            self.image_extensions.append('.tif')


class PathParser:
    """
    Contains the methods for hashing files and directories
    """

    def __init__(self, path, image_extensions):
        self.path = path
        self.image_extensions = image_extensions

        self.files = []
        self.subdirs = []

    def walker(self):
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


def get_application_path():
    """
    Gets the location of the executable file for storing data
    :return: None
    """

    application_path = None

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)

    elif __file__:
        application_path = os.path.dirname(__file__)

    return application_path


def initialize_config(path):
    """
    Sets up a new config file, or loads one if it already exists at the exe directory
    :param path: path to config file
    :return: None
    """

    config_file_path = os.path.join(path, 'ivcs.ini')

    config = configparser.ConfigParser()

    # Set default options
    config['DEFAULT'] = {"ImageExtensions": ['.img', '.tif'],
                         "ChangeDetectMethod": "Timestamp",
                         "Username": "UNSET"}

    config['BRANCHES'] = {"TestBranch": "~/DEV/ivcs/testBranch"}

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)


def db_init(path):
    """
    Initializes the database
    :return: SQLAlchemy session object
    """

    imagery_database = ImageryDatabase(path)
    db_session = imagery_database.load_session()  # Get the session object

    return db_session


def main():
    """
    Starts the program
    :return: None
    """

    # Create config file
    app_dir = get_application_path()

    # Set up DB
    db_init(app_dir)

    if not os.path.exists(os.path.join(app_dir, 'ivcs.ini')):
        initialize_config(app_dir)

    app = ivcs_mainwindow.QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
