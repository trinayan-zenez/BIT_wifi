# Copyright (c) 2025 Trinayan Chaduvula.
# This file is part of hostel-wifi-login.
# Licensed under the GNU General Public License v3.0
# See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.html
# Unauthorized copying, distribution, or modification is prohibited.
import subprocess
import requests
import time
import threading
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

# ----ONLY CHANGE THESE VALUES----#
USERNAME_VALUE = "xxxxxxxxxx"  # Replace with your actual username
PASSWORD_VALUE = "xxxxxxxxxx"  # Replace with your actual password

SSID_LIST = [
    "Hostel-1",
    "Hostel-2",
    "Hostel-3",
    "Hostel-4"
    "College-WiFi",
  # Add more if needed
]
# ----DO NOT CHANGE BELOW UNLESS YOU KNOW WHAT YOU ARE DOING----#

PORTAL_IP        = "192.168.0.2"
PORTAL_PORT      = 8090
LOGIN_URL        = f"http://{PORTAL_IP}:{PORTAL_PORT}/login.xml"
LOGOUT_URL       = f"http://{PORTAL_IP}:{PORTAL_PORT}/logout.xml"
MAX_SCAN_TRIES   = 10
MAX_CONNECT_WAIT = 30
MAX_PORTAL_WAIT  = 20

# ── Icon ──────────────────────────────────────────────────────────────────────

def create_icon_image(color="blue"):
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    fill = {
        "blue":   (30, 120, 255),
        "green":  (30, 200, 80),
        "red":    (220, 50, 50),
        "gray":   (130, 130, 130),
        "orange": (255, 160, 30),
    }
    draw.ellipse([4, 4, 60, 60], fill=fill.get(color, (30, 120, 255)))
    return img

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr

def get_current_ssid():
    output = run("netsh wlan show interfaces")
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("SSID") and "BSSID" not in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                return parts[1].strip()
    return None

def scan_available_networks():
    output = run("netsh wlan show networks mode=bssid")
    found  = set()
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("SSID") and "BSSID" not in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                ssid = parts[1].strip()
                if ssid:
                    found.add(ssid)
    return found

def find_best_network(ssid_list, tries=MAX_SCAN_TRIES):
    for attempt in range(1, tries + 1):
        visible = scan_available_networks()
        for ssid in ssid_list:
            if ssid in visible:
                return ssid
        time.sleep(3)
    return None

def connect_network(ssid):
    run("netsh wlan disconnect")
    time.sleep(1)
    run(f'netsh wlan connect name="{ssid}"')

def wait_for_connection(ssid, timeout=MAX_CONNECT_WAIT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        output = run("netsh wlan show interfaces")
        if ssid in output and "connected" in output.lower():
            return True
        time.sleep(2)
    return False

def wait_for_portal(ip, port, timeout=MAX_PORTAL_WAIT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            requests.get(f"http://{ip}:{port}/", timeout=3)
            return True
        except:
            pass
        time.sleep(2)
    return False

def login(username, password):
    session = requests.Session()
    payload = {
        "mode":        "191",
        "username":    username,
        "password":    password,
        "a":           str(int(time.time() * 1000)),
        "producttype": "0"
    }
    try:
        response = session.post(LOGIN_URL, data=payload, timeout=10)
        if "You are signed in" in response.text or "logged" in response.text.lower():
            return True, "Login successful!"
        elif "Invalid" in response.text or "failed" in response.text.lower():
            return False, "Login failed — check credentials."
        else:
            return False, "Ambiguous response from portal."
    except Exception as e:
        return False, f"Error: {e}"

def logout(username):
    try:
        payload = {"mode": "193", "username": username, "producttype": "0"}
        requests.post(LOGOUT_URL, data=payload, timeout=5)
    except:
        pass
    run("netsh wlan disconnect")

# ── Tray actions ──────────────────────────────────────────────────────────────

def do_connect(icon, _):
    def task():
        icon.icon  = create_icon_image("gray")
        icon.title = "Scanning..."

        ssid = find_best_network(SSID_LIST)
        if not ssid:
            icon.icon  = create_icon_image("red")
            icon.title = "No network found"
            icon.notify("None of your listed networks are visible.", "Connect Failed")
            return

        icon.title = f"Connecting to {ssid}..."
        connect_network(ssid)

        if not wait_for_connection(ssid):
            icon.icon  = create_icon_image("red")
            icon.title = "Connection timed out"
            icon.notify(f"Could not associate with '{ssid}'.", "Connect Failed")
            return

        icon.title = "Waiting for portal..."
        if not wait_for_portal(PORTAL_IP, PORTAL_PORT):
            icon.icon  = create_icon_image("red")
            icon.title = "Portal unreachable"
            icon.notify("Portal IP never responded.", "Connect Failed")
            return

        icon.title = "Logging in..."
        success, msg = login(USERNAME_VALUE, PASSWORD_VALUE)

        if success:
            icon.icon  = create_icon_image("green")
            icon.title = f"Online — {ssid}"
            icon.notify(msg, "Connected ✓")
        else:
            icon.icon  = create_icon_image("red")
            icon.title = "Login failed"
            icon.notify(msg, "Connect Failed")

    threading.Thread(target=task, daemon=True).start()


def do_disconnect(icon, _):
    def task():
        icon.icon  = create_icon_image("orange")
        icon.title = "Disconnecting..."

        ssid = get_current_ssid()
        logout(USERNAME_VALUE)

        icon.icon  = create_icon_image("blue")
        icon.title = "Disconnected"
        icon.notify(
            f"Logged out from '{ssid}'." if ssid else "Disconnected.",
            "Offline"
        )

    threading.Thread(target=task, daemon=True).start()

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    icon = pystray.Icon(
        name  = "wifi_login",
        icon  = create_icon_image("blue"),
        title = "WiFi Login",
        menu  = pystray.Menu(
            item("Connect",    do_connect,    default=True),
            item("Disconnect", do_disconnect),
        )
    )
    icon.run()
