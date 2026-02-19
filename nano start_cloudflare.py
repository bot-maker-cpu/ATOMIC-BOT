import subprocess
import re
import time

URL_FILE = "public_url.txt"

process = subprocess.Popen(
    ["cloudflared", "tunnel", "--url", "http://localhost:5005"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

for line in process.stdout:
    print(line)

    match = re.search(r"https://[-a-z0-9]+\.trycloudflare\.com", line)
    if match:
        url = match.group(0)
        print("FOUND URL:", url)

        with open(URL_FILE, "w") as f:
            f.write(url)

        break

while True:
    time.sleep(999)
