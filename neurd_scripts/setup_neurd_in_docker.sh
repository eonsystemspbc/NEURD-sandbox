#!/bin/bash

# Install NEURD and dependencies
cd /
apt-get install pandoc
pip3 install pypandoc
git clone https://github.com/TheSalocin/datasci_tools.git
pip3 install -e ./datasci_tools
git clone https://github.com/TheSalocin/NEURD.git
pip3 install -e ./NEURD/

