import subprocess
import time

subprocess.Popen(["python", "server.py"])
time.sleep(2)

subprocess.Popen(["python", "start_cloudflare.py"])
time.sleep(5)

subprocess.run(["python", "atomic_panel.py"])
