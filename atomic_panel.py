import os
import subprocess
import sys
import random
import time
import json
import requests
import os
import requests

BOT_FILE = "067final.py"
BOT_URL = "https://github.com/bot-maker-cpu/dying/blob/main/067final.py"

def download_core():
    if not os.path.exists(BOT_FILE):
        print("⬇ Downloading core system...")
        r = requests.get(BOT_URL, timeout=20)

        if r.status_code != 200:
            print("❌ Failed to download core")
            exit()

        with open(BOT_FILE, "w", encoding="utf-8") as f:
            f.write(r.text)

        print("✅ Core installed")

download_core()
# --- CONFIG ---
CORRECT_PASSWORD = "sarthak123"
PUBLIC_URL = "https://shakespeare-radiation-victorian-eternal.trycloudflare.com"  # <-- CHANGE WHEN LINK CHANGES

# --- COLORS ---
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ----------------------------
# VOICE (Optional)
# ----------------------------

def speak(text):
    try:
        subprocess.run(["espeak", text], stderr=subprocess.DEVNULL)
    except:
        pass

# ----------------------------
# BANNER
# ----------------------------

def print_banner():
    banner = f"""
{CYAN}{BOLD}
 █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗
██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝
███████║   ██║   ██║   ██║██╔████╔██║██║██║
██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║
██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗
╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝
ATOMIC PROTON ENTERPRISE
{RESET}
"""
    print(banner)

# ----------------------------
# WEB VERIFICATION SYSTEM
# ----------------------------

def web_verification_phase():
    code = f"atomic-{random.randint(1000000,9999999)}"

    print("\nSubmit this code at the verification website:")
    print(PUBLIC_URL)
    print("\nYour Code:", code)

    while True:
        try:
            with open("codes.json","r") as f:
                db = json.load(f)

            if code in db.get("approved", {}):
                generated_password = db["approved"][code]

                print("\n✔ Code Approved!")
                print("Your Access Password:", generated_password)

                # Now ask user to enter it
                entered = input("Enter the password to continue: ")

                if entered == generated_password:
                    print("Access Granted.")
                    break
                else:
                    print("Wrong password.")

            else:
                print("Waiting for approval...")
                time.sleep(5)

        except:
            print("Waiting for verification server...")
            time.sleep(5)

# ----------------------------
# INSTALL PACKAGES
# ----------------------------

def install_packages():
    print(f"\n{YELLOW}[Installing Required Packages]{RESET}")
    packages = ["discord.py", "openai", "pytz", "dateparser", "aiohttp", "python-dotenv"]

    for pkg in packages:
        print(f"{CYAN}Installing {pkg}...{RESET}")
        subprocess.call([sys.executable, "-m", "pip", "install", pkg])

    print(f"{GREEN}✅ System Ready.{RESET}")
LOCK_FILE = "bot.lock"

def is_bot_running():
    return os.path.exists(LOCK_FILE)
# ----------------------------
# MAIN MENU
# ----------------------------
def main_menu():
    import uuid
    while True:
        print(f"\n{BOLD}--- ATOMIC PROTON MENU ---{RESET}")
        print("1. Setup the Bot (Config IDs)")
        print("2. View Features")
        print("3. Suggest a Feature")
        print("4. Get Bot Invite URL")
        print("5. Run Bot")
        print("0. Exit")

        choice = input(f"\n{CYAN}Select an option (0-5): {RESET}")

        # ---------------- OPTION 1 ----------------
        if choice == '1':
            owner_ids = input("Enter Owner IDs: ")
            guild_id = input("Enter Guild ID: ")
            with open("067final.py", "a") as f:
                f.write(f"\nOWNER_IDS = [{owner_ids}]\nGUILD_ID = {guild_id}\n")
            print(f"{GREEN}✅ Config loaded!{RESET}")

        # ---------------- OPTION 2 ----------------
        elif choice == '2':
            print(f"{YELLOW}Features: AI RPG, Flag Game, Timezone Sync, Anime GIFs, XP System.{RESET}")

        # ---------------- OPTION 3 ----------------
        elif choice == '3':
            suggestion = input("Type your suggestion: ")
            try:
                requests.post(
                    PUBLIC_URL + "/suggest",
                    data={"suggestion": suggestion}
                )
                print(f"{GREEN}✅ Suggestion sent successfully!{RESET}")
            except Exception as e:
                print(f"{RED}⚠ Could not connect to suggestion server: {e}{RESET}")

        # ---------------- OPTION 4 ----------------
        elif choice == '4':
            invite = "https://discord.com/oauth2/authorize?client_id=1466838204442345755&permissions=8&scope=bot"
            print(f"{BLUE}🔗 Bot Invite URL:{RESET}")
            print(invite)

        # ---------------- OPTION 5 ----------------
        elif choice == '5':
            device_id = str(uuid.uuid4())

            try:
                response = requests.post(
                    PUBLIC_URL + "/start",
                    data={"device": device_id}
                ).json()

                if response.get("allowed"):
                    print(f"{GREEN}✅ Bot starting...{RESET}")
                    subprocess.run([sys.executable, "067final.py", device_id])

                    requests.post(
                        PUBLIC_URL + "/stop",
                        data={"device": device_id}
                    )

                else:
                    print(f"{YELLOW}⚠ Bot already running on another device.{RESET}")
                    force = input(f"{CYAN}Force takeover as Owner? (y/n): {RESET}")

                    if force.lower() == "y":
                        password = input("Enter Owner Password: ")

                        force_response = requests.post(
                            PUBLIC_URL + "/force",
                            data={"device": device_id, "password": password}
                        ).json()

                        if force_response.get("allowed"):
                            print(f"{GREEN}🔥 Owner takeover successful.{RESET}")
                            subprocess.run([sys.executable, "067final.py", device_id])

                            requests.post(
                                PUBLIC_URL + "/stop",
                                data={"device": device_id}
                            )
                        else:
                            print(f"{RED}❌ Wrong Owner Password.{RESET}")

            except Exception as e:
                print(f"{RED}⚠ Connection error: {e}{RESET}")
        # ---------------- EXIT ----------------
        elif choice == '0':
            print(f"{YELLOW}Exiting... Goodbye!{RESET}")
            break

        else:
            print(f"{RED}Invalid option. Try again.{RESET}")
# ----------------------
# MAIN
# ----------------------

if __name__ == "__main__":
    print_banner()
    web_verification_phase()   # FIRST verification
    install_packages()
    main_menu()

    # Start backend systems
    import server
    import bot_main
