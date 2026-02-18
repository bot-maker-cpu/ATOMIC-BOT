import os
import subprocess
import sys
import random
import time

# --- CONFIG ---
CORRECT_PASSWORD = "sarthak123"
OWNER_DISCORD_ID = "avrothegamer"

# --- COLORS ---
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def speak(text):
    """Voice status using espeak."""
    try:
        subprocess.run(["espeak", text], stderr=subprocess.DEVNULL)
    except:
        pass

def print_banner():
    banner = f"""
    {CYAN}{BOLD}
     █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗    ██████╗ ██████╗  ██████╗ ████████╗ ██████╗ ███╗   ██╗
    ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝    ██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗████╗  ██║
    ███████║   ██║   ██║   ██║██╔████╔██║██║██║         ██████╔╝██████╔╝██║   ██║   ██║   ██║   ██║██╔██╗ ██║
    ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║         ██╔═══╝ ██╔══██╗██║   ██║   ██║   ██║   ██║██║╚██╗██║
    ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗    ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝
    {RESET}
    """
    print(banner)

def verify_user():
    print(f"{BOLD}{YELLOW}🔐 SECURITY CHECK REQUIRED{RESET}")
    speak("Please enter the access password.")
    
    attempts = 3
    while attempts > 0:
        pwd = input(f"{CYAN}Enter Password: {RESET}")
        if pwd == CORRECT_PASSWORD:
            print(f"{GREEN}✔ Access Granted!{RESET}\n")
            speak("Access granted.")
            return True
        else:
            attempts -= 1
            print(f"{RED}❌ Incorrect password! {attempts} attempts left.{RESET}")
    sys.exit()

def dm_instruction_phase():
    """Forces the user to generate a code and DM the owner."""
    code = f"atomic-sarthak-{random.randint(1000000, 9999999)}"
    
    print(f"{BOLD}{YELLOW}📢 MANDATORY STEP: DM THE OWNER{RESET}")
    print(f"To use this software, you must send your verification code to the owner.")
    print(f"\n{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{YELLOW}YOUR UNIQUE CODE:{RESET} {GREEN}{code}{RESET}")
    print(f"{YELLOW}DISCORD OWNER ID:{RESET} {BOLD}{OWNER_DISCORD_ID}{RESET}")
    print(f"{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
    
    speak(f"Code generated. You must now direct message the ID {OWNER_DISCORD_ID} with this code to be accepted.")
    
    while True:
        check = input(f"{CYAN}Have you sent the DM to {OWNER_DISCORD_ID}? (y/n): {RESET}").lower()
        if check == 'y':
            print(f"{GREEN}Proceeding to package installation...{RESET}")
            break
        else:
            print(f"{RED}Please send the DM first to continue.{RESET}")

def install_packages():
    print(f"\n{YELLOW}[1/3] Installing essential packages...{RESET}")
    speak("Starting installation of required packages.")
    # Based on your files
    packages = ["discord.py", "openai", "pytz", "dateparser", "aiohttp", "python-dotenv"]
    
    for pkg in packages:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    
    print(f"{GREEN}✅ Status: System Ready.{RESET}")
    speak("Installation complete.")

def main_menu():
    while True:
        print(f"\n{BOLD}--- ATOMIC PROTON SETUP MENU ---{RESET}")
        print("1. Setup the Bot (Config IDs)")
        print("2. Ask about Features")
        print("3. Suggest a Feature")
        print("4. Get Bot Invite URL")
        print("5. Run Bot (Only if offline)")
        print("0. Exit")
        
        choice = input(f"\n{CYAN}Select an option (0-5): {RESET}")

        if choice == '1':
            owner_ids = input("Enter Owner IDs: ")
            guild_id = input("Enter Guild ID: ")
            with open("067final.py", "a") as f:
                f.write(f"\nOWNER_IDS = [{owner_ids}]\nGUILD_ID = {guild_id}\n")
            print(f"{GREEN}✅ Config loaded!{RESET}")

        elif choice == '2':
            print(f"\n{YELLOW}Features: AI RPG, Flag Game, Timezone Sync, Anime GIFs, and XP System.{RESET}")

        elif choice == '3':
            suggestion = input("Type your suggestion: ")
            print(f"{GREEN}Suggestion recorded for {OWNER_DISCORD_ID}.{RESET}")

        elif choice == '4':
            print(f"{BOLD}{BLUE}🔗 Invite URL: https://discord.com/oauth2/authorize?client_id=1466838204442345755{RESET}")

        elif choice == '5':
            print(f"{YELLOW}Launching bot...{RESET}")
            subprocess.run([sys.executable, "067final.py"])

        elif choice == '0':
            break

if __name__ == "__main__":
    print_banner()
    verify_user()          # 1. Check Password
    dm_instruction_phase() # 2. Force DM to avrothegamer
    install_packages()     # 3. Install packages
    
    # Optional Server Join
    if input(f"\n{YELLOW}Join our support server? (y/n): {RESET}").lower() == 'y':
        print(f"{BLUE}Link: https://discord.gg/TpJnCQCux{RESET}")
        
    main_menu()            # 4. Final Menu

