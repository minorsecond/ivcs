"""
Imagery Version Control System
2016 Robert Ross Wardrup
"""

import os
import configparser
import sys
import ast
import shutil
import hashlib
import datetime
import logging
from PyQt4.QtCore import QThread
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from database import ImageryDatabase, DatabaseQueries
from gui import commit_message_window, ivcs_mainwindow, settings_window, view_message_window, \
    CheckoutStatus, ManageProjectsWindow
import compressor
import filesystem_utils

class MainWindow(ivcs_mainwindow.QtGui.QMainWindow, ivcs_mainwindow.Ui_MainWindow):
    def __init__(self):
        ivcs_mainwindow.QtGui.QMainWindow.__init__(self)
        ivcs_mainwindow.Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.image_extensions = []
        self.general_functions = filesystem_utils.GeneralFunctions()
        self.app_dir = self.general_functions.get_application_path()

        if not os.path.exists(os.path.join(self.app_dir, 'ivcs.ini')):
            logging.warning("Couldn't find configuration file at {}, after it should have been "
                            "automatically created.".format(self.app_dir))

            # Disable all GUI elements until a branch is set and scanned
            self.RemoteChangesListView.setEnabled(False)
            self.LocalFileListVIew.setEnabled(False)
            self.RemoteChangesListView.setEnabled(False)
            self.LocalChangesListView.setEnabled(False)

            self.CheckoutButton.setEnabled(False)
            self.ViewRemoteCommitButton.setEnabled(False)
            self.CommitButton.setEnabled(False)
            self.PushButton.setEnabled(False)

        else:
            # Load current settings
            self.config_file_path = os.path.join(self.app_dir, 'ivcs.ini')
            self.config = configparser.ConfigParser()
            self.config.read(self.config_file_path)

            self.change_detection_method = self.config.get("settings", "changedetectmethod")
            self.username = self.config.get("settings", "username")
            self.image_extensions = ast.literal_eval(self.config.get("settings", "imageextensions"))
            self.storage_path = self.config.get("settings", "datapath")

        # Menu Bar Actions
        self.actionSettings.triggered.connect(self.handle_settings_click)
        self.actionManage_Projects.triggered.connect(self.handle_manage_projects_click)

        self.open_database(self.username)

    def handle_settings_click(self):
        """
        Handles user clicking the settings button in the menu bar
        :return: None
        """

        settings = SettingsWindow()
        settings.show()
        settings.exec_()

    def handle_new_branch_click(self):
        """
        Handles user clicking the new branch button in the menu bar
        :return: None
        """

        pass

    def open_database(self, username):
        """
        Opens up the DB
        :return: None
        """
        self.username = username
        logging.info("Querying the database for user projects.")

        queries = DatabaseQueries(self.app_dir)
        projects = queries.query_projects_for_user(self.username)

        if projects is ValueError:  # Could not find any users matching the name
            logging.error("Could not find any rows in Users DB for current username.")
        else:
            for project in projects:
                print(project)

        #self.fs_walker = filesystem_utils.FileSystemWalker(self.storage_path, self.image_extensions)
        #self.files = self.fs_walker

    def handle_manage_projects_click(self):
        """
        Handle user clicking manage projects
        :return: None
        """

        proj_window = ProjectsWindow()
        proj_window.show()
        proj_window.exec_()


class SettingsWindow(settings_window.QtGui.QDialog, settings_window.Ui_Dialog):
    """
    Settings Window
    """

    def __init__(self):
        settings_window.QtGui.QDialog.__init__(self)
        settings_window.Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.image_extensions = []
        self.username = None
        self.storage_path = None
        self.change_detection_method = None

        fs_utils = filesystem_utils.GeneralFunctions()
        self.main_window = MainWindow()

        # Load current settings
        self.app_dir = fs_utils.get_application_path()
        self.config_file_path = os.path.join(self.app_dir, 'ivcs.ini')
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)

        self.change_detection_method = self.config.get("settings", "changedetectmethod")
        self.username = self.config.get("settings", "username")
        self.image_extensions = ast.literal_eval(self.config.get("settings", "imageextensions"))
        self.storage_path = self.config.get("settings", "datapath")

        if self.change_detection_method == "hash":
            self.UseChecksums.setChecked(True)
        elif self.change_detection_method == "modification_time":
            self.UseOSModifiedDate.setChecked(True)
        else:
            logging.error("Invalid value in change_detection_method.")
            raise ValueError

        if ".img" in self.image_extensions:
            self.ImgExtensionCheckBox.setChecked(True)
        if ".tif" in self.image_extensions:
            self.TifExtensionCheckBox.setChecked(True)

        self.UserNameEntry.setText(self.username)
        self.DataStoragePathEntry.setText(self.storage_path)

        # Buttonbox actions
        self.buttonBox.button(settings_window.QtGui.QDialogButtonBox.Ok).\
            clicked.connect(self.save_settings)

    def save_settings(self):
        """
        Save settings into the .ini file
        :return: None
        """
        self.image_extensions = []
        self.change_detection_method = None
        self.username = None
        self.storage_path = None

        image_type_checkboxes = [self.ImgExtensionCheckBox, self.TifExtensionCheckBox]

        if self.UseChecksums.isChecked():
            self.change_detection_method = "hash"
        elif self.UseOSModifiedDate.isChecked():
            self.change_detection_method = "modification_time"

        for checkbox in image_type_checkboxes:
            if checkbox.isChecked():
                text = checkbox.text()
                if text not in self.image_extensions:
                    self.image_extensions.append(checkbox.text())

        self.username = self.UserNameEntry.text()
        self.storage_path = self.DataStoragePathEntry.text()

        # Make sure all fields contain a value before writing to file
        if self.UseChecksums or self.UseOSModifiedDate:
            if self.ImgExtensionCheckBox or self.TifExtensionCheckBox:
                if len(self.UserNameEntry.text()) >= 2:
                    if len(self.DataStoragePathEntry.text()) >= 2:
                        try:
                            self.write_config()
                            self.main_window.open_database(self.username)
                        except Exception as e:
                            logging.error("Could not write to configuration file. The write_config "
                                          "function returned: {}".format(e))
                            print(e)

    def write_config(self):
        """
        Saves the new settings to the configuration file
        :return: Disk IO
        """

        # Set default options
        self.config['settings'] = {"username": self.username,
                                   "ImageExtensions": self.image_extensions,
                                   "ChangeDetectMethod": self.change_detection_method,
                                   "DataPath": self.storage_path}

        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)

        logging.info("Updated configuration file at {}".format(self.config_file_path))


class ProjectsWindow(ManageProjectsWindow.QtGui.QDialog,
                     ManageProjectsWindow.Ui_ManageProjectsWindow):

    def __init__(self):
        super(ProjectsWindow, self).__init__()

        ManageProjectsWindow.QtGui.QDialog.__init__(self)
        ManageProjectsWindow.Ui_ManageProjectsWindow.__init__(self)
        self.setupUi(self)

        # Set the global application path
        general_functions = filesystem_utils.GeneralFunctions()
        self.app_dir = general_functions.get_application_path()

        # Get list of projects
        queries = DatabaseQueries(self.app_dir)
        projects = queries.get_all_projects()

        for project in projects:
            project_id = project[0]
            project_name = project[1]
            self.ProjectsList.addItem(project_name)


class CheckoutStatusWindow(CheckoutStatus.QtGui.QDialog, CheckoutStatus.Ui_Dialog):
    """
    Status window for checking out files
    """

    def __init__(self):
        super(CheckoutStatusWindow, self).__init__()
        CheckoutStatus.QtGui.QDialog.__init__(self)
        CheckoutStatus.Ui_Dialog.__init__(self)
        self.setupUi(self)

    def update_progress_bar(self, read, total):
        """
        Updates the progress bar
        :param read: Amount read (int)
        :param total: Total length(int)
        :return: None
        """

        print("Read: {}".format(read))
        print("Total: {}".format(total))


class IoThread(QThread):
    """
    Run the disk IO functions in a separate thread
    """

    def __init__(self, path):
        QThread.__init__(self)
        self.path = path

    def __del__(self):
        self.wait()

    def run(self):
        initialize_config(self.path)


def initialize_config(path):
    """
    Sets up a new config file, or loads one if it already exists at the exe directory
    :param path: path to config file
    :return: None
    """

    config_file_path = os.path.join(path, 'ivcs.ini')

    config = configparser.ConfigParser()

    # Set default options
    config['settings'] = {"ImageExtensions": ['.img', '.tif'],
                          "ChangeDetectMethod": "modification_time",
                          "Username": "UNSET",
                          "datapath": "~"}

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)


def db_init(path):
    """
    Initializes the database
    :return: SQLAlchemy session object
    """

    imagery_database = ImageryDatabase(path)
    db_session = imagery_database.load_session()  # Get the session object

    logging.info("Initialized database at {}".format(path))

    return db_session


def logger():
    """
    Sets up the logfile
    :return: None
    """

    fs_utils = filesystem_utils.GeneralFunctions()
    path = fs_utils.get_application_path()
    logfile = os.path.join(path, 'IVCS.log')
    log = logging.basicConfig(filename=logfile, format='%(asctime)s %(levelname)s -> %(message)s',
                              level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

    return log


def main():
    """
    Starts the program
    :return: None
    """

    logger()
    logging.info("IVCS started.")

    # TESTING
    io = filesystem_utils.FileCopier("/Users/rwardrup/Downloads/pycharm-professional-2016.2.3.dmg")
    io.run()

    general_functions = filesystem_utils.GeneralFunctions()

    # Create config file
    app_dir = general_functions.get_application_path()

    if not os.path.exists(os.path.join(app_dir, 'ivcs.ini')):
        initialize_config(app_dir)
        logging.info("Created configuration file at {}".format(app_dir))

    app = ivcs_mainwindow.QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
