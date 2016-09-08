"""
Imagery Version Control System
2016 Robert Ross Wardrup
"""

import os
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
        #self.setFixedHeight(self.size())

        # Disable all GUI elements until a branch is set and scanned
        self.RemoteFileList.setEnabled(False)
        self.LocalFileList.setEnabled(False)
        self.RemoteChangeList.setEnabled(False)
        self.LocalChangeList.setEnabled(False)

        self.CheckoutButton.setEnabled(False)
        self.ViewRemoteCommitButton.setEnabled(False)
        self.CommitButton.setEnabled(False)
        self.PushButton.setEnabled(False)

if __name__ == '__main__':
    app = ivcs_mainwindow.QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
