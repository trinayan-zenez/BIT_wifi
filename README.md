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
