![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
# BITM WiFi Auto-Login

Sits in your system tray. Right-click → Connect or Disconnect.

## Setup
pip install -r requirements.txt

## Configure
Create a config.py (never commit this):
    USERNAME_VALUE = "your_username"
    PASSWORD_VALUE = "your_password"

Add your networks to SSID_LIST in wifi_login.pyw.

## Run
pythonw wifi_login.pyw

## Auto-start with Windows
Press Win+R → type shell:startup → drop a shortcut to wifi_login.pyw there
## License
Copyright (c) 2025 Trinayan Chaduvula(github.com/trinayan-zenez). All rights reserved.  
Licensed under [GNU GPLv3](LICENSE). You may not copy, distribute, or modify 
this project without attribution and keeping it open source.
