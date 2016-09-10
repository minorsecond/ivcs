#!/usr/bin/env bash

# Load the venv
source ~/miniconda3/bin/activate ivcs

# Create the GUI files
pyuic4 gui/ivcs_mainwindow.ui -o gui/ivcs_mainwindow.py
pyuic4 gui/settings_window.ui -o gui/settings_window.py
pyuic4 gui/view_message_window.ui -o gui/view_message_window.py
pyuic4 gui/commitmessage_window.ui -o gui/commit_message_window.py
pyuic4 gui/CreateBranchWindow.ui -o gui/CreateBranchWindow.py
pyuic4 gui/CheckoutStatus.ui -o gui/CheckoutStatus.py
pyuic4 gui/ManageProjectsWindow.ui -o gui/ManageProjectsWindow.py
pyuic4 gui/AddProject.ui -o gui/AddProject.py
pyuic4 gui/ErrorMessage.ui -o gui/ErrorMessage.py
pyuic4 gui/NewUserRegistrationWindow.ui -o gui/NewUserRegistrationWindow.py
pyuic4 gui/LoginWindow.ui -o gui/LoginWindow.py