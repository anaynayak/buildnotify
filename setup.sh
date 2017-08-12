#!/bin/bash

sudo apt-get update
sudo apt-get install -y ubuntu-desktop xinit unity
sudo apt-get install -y python-pyqt5 pyqt5-dev-tools python-tz python-dateutil qtdeclarative5-dev qttools5-dev-tools python-pip python-keyring
sudo pip install paver
sudo pip install -r test-requirements.txt

