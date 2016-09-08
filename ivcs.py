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
from gui import commit_message_window, ivcs_mainwindow, settings_window, view_message_window


class MainWindow(ivcs_mainwindow.QtGui.QMainWindow, ivcs_mainwindow.Ui_MainWindow):
    def __init__(self):
        ivcs_mainwindow.QtGui.QMainWindow.__init__(self)
        ivcs_mainwindow.Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # elf.setFixedHeight(self.size())

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


def main():
    """
    Starts the program
    :return: None
    """

    # Create config file
    app_dir = get_application_path()

    if not os.path.exists(os.path.join(app_dir, 'ivcs.ini')):
        initialize_config(app_dir)

    app = ivcs_mainwindow.QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
