#!/usr/bin/env python3
"""
ATOMIC-BOT Main Entry Point

This is the main file for ATOMIC-BOT. Always run this file first to start the application.
"""
import subprocess
import sys
import time

def main():
    print("=" * 50)
    print("🤖 ATOMIC-BOT - Main Launcher")
    print("=" * 50)
    
    try:
        print("\n[1/3] Starting server.py...")
        subprocess.Popen(["python", "server.py"])
        time.sleep(2)
        
        print("[2/3] Starting start_cloudflare.py...")
        subprocess.Popen(["python", "start_cloudflare.py"])
        time.sleep(5)
        
        print("[3/3] Starting atomic_panel.py...")
        subprocess.run(["python", "atomic_panel.py"])
        
    except KeyboardInterrupt:
        print("\n\n⚠️  ATOMIC-BOT stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running ATOMIC-BOT: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
