#!/usr/bin/env bash

# Load the venv
source ~/miniconda3/bin/activate ivcs

# Create the GUI files
pyuic4 gui/ivcs_mainwindow.ui -o gui/ivcs_mainwindow.py
pyuic4 gui/settings_window.ui -o gui/settings_window.py
pyuic4 gui/view_message_window.ui -o gui/view_message_window.py
pyuic4 gui/commitmessage_window.ui -o gui/commit_message_window.py

