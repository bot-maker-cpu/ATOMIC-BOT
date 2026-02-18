import os
import sys
import json
import uuid
import time
import hashlib
import random
import platform
import subprocess
from datetime import datetime, timedelta

# ==============================
# CONFIG
# ==============================

LOCK_FILE = ".atomic.lock"
LICENSE_FILE = "license.json"
MAIN_FILE = "067final.py"
SECRET_KEY = "ATOMIC_PRIVATE_SECRET_2026"

# ==============================
# DEVICE ID
# ==============================

def get_device_id():
    raw = platform.node() + platform.system() + str(uuid.getnode())
    return hashlib.sha256(raw.encode()).hexdigest()

# ==============================
# SINGLE INSTANCE
# ==============================

def create_lock():
    if os.path.exists(LOCK_FILE):
        print("Atomic is already running.")
        sys.exit()
    with open(LOCK_FILE,"w") as f:
        f.write(str(os.getpid()))

def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# ==============================


# ==============================
# LICENSE SYSTEM
# ==============================

def generate_signature(device_id, expiry):
    raw = device_id + expiry + SECRET_KEY
    return hashlib.sha256(raw.encode()).hexdigest()

def create_license(days_valid=7):
    device_id = get_device_id()
    expiry_date = (datetime.now() + timedelta(days=days_valid)).strftime("%Y-%m-%d")

    signature = generate_signature(device_id, expiry_date)

    data = {
        "device_id": device_id,
        "expiry": expiry_date,
        "signature": signature
    }

    with open(LICENSE_FILE,"w") as f:
        json.dump(data,f,indent=4)

    print("License created. Valid for", days_valid, "days.")

def validate_license():
    if not os.path.exists(LICENSE_FILE):
        print("No license found.")
        return False

    with open(LICENSE_FILE,"r") as f:
        data = json.load(f)

    device_id = get_device_id()

    if data["device_id"] != device_id:
        print("License locked to another device.")
        return False

    expected_sig = generate_signature(data["device_id"], data["expiry"])

    if expected_sig != data["signature"]:
        print("License tampering detected.")
        return False

    expiry_date = datetime.strptime(data["expiry"], "%Y-%m-%d")

    if datetime.now() > expiry_date:
        print("License expired.")
        return False

    return True

# ==============================
# PACKAGE INSTALL
# ==============================

def install_packages():
    subprocess.call("pip install -r requirements.txt", shell=True)

# ==============================
# COMMAND LIST
# ==============================

def show_commands():
    print("""
========== ATOMIC PROTON COMMAND LIST ==========

ADMIN:
/ban
/kick
/mute
/unmute

FUN:
/anime
/animegif
/meme
/count

UTILITY:
/detect
/help
/ping
/serverinfo

RPG:
/battle
/detective
/mission

==============================================
""")

# ==============================
# MENU
# ==============================

def menu():
    while True:
        print("""
1. Setup License
2. Install Packages
3. View Command List
4. Run Bot
5. Exit
""")

        choice = input("> ").strip()

        if choice == "1":
            create_license(7)

        elif choice == "2":
            install_packages()

        elif choice == "3":
            show_commands()

        elif choice == "4":
            print("Launching Atomic Core...")
            os.system("python 067final.py")

        elif choice == "5":
            break

# ==============================
# BANNER
# ==============================

def banner():
    print("""
█████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗
██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝
███████║   ██║   ██║   ██║██╔████╔██║██║██║     
██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║     
██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗
╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝
           ATOMIC ENTERPRISE EDITION
""")

# ==============================
# MAIN
# ==============================

def main():
    banner()

    create_lock()

    if not validate_license():
        print("Invalid or missing license.")
        remove_lock()
        sys.exit()

    menu()

    remove_lock()

if __name__ == "__main__":
    try:
        main()
    finally:
        remove_lock()
