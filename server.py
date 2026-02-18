import random
import string
from flask import Flask, request, redirect
import json
import os
from flask import Flask, request, jsonify
import hashlib


app = Flask(__name__)
OWNER_PASSWORD = "atomic@123"  # Change this to your secret
OWNER_HASH = hashlib.sha256(OWNER_PASSWORD.encode()).hexdigest()

bot_state = {
    "status": "offline",
    "device": None
}
@app.route("/status")
def status():
    return jsonify(bot_state)
@app.route("/start", methods=["POST"])
def start():
    device = request.form.get("device")

    if bot_state["status"] == "offline":
        bot_state["status"] = "online"
        bot_state["device"] = device
        return jsonify({"allowed": True})

    return jsonify({"allowed": False})
@app.route("/force", methods=["POST"])
def force():
    device = request.form.get("device")
    password = request.form.get("password")

    if hashlib.sha256(password.encode()).hexdigest() != OWNER_HASH:
        return jsonify({"allowed": False})

    bot_state["status"] = "online"
    bot_state["device"] = device

    return jsonify({"allowed": True})
@app.route("/stop", methods=["POST"])
def stop():
    device = request.form.get("device")

    if bot_state["device"] == device:
        bot_state["status"] = "offline"
        bot_state["device"] = None
        return jsonify({"stopped": True})

    return jsonify({"stopped": False})


DATABASE = "codes.json"

if not os.path.exists(DATABASE):
    with open(DATABASE, "w") as f:
        json.dump({"pending": [], "approved": {}}, f)


def load_db():
    with open(DATABASE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)

def generate_password():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@app.route("/")
def home():
    return """
    <h2>Submit Verification Code</h2>
    <form method="POST" action="/submit">
        <input name="code">
        <button type="submit">Submit</button>
    </form>
    """

@app.route("/submit", methods=["POST"])
def submit():
    code = request.form["code"]
    db = load_db()

    if code not in db["pending"]:
        db["pending"].append(code)
        save_db(db)

    return "Code submitted. Wait for approval."

from flask import request

ADMIN_PASSWORD = "atomic@123"

@app.route("/admin")
def admin():
    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Unauthorized."

    db = load_db()
    response = "<h2>Pending Codes</h2>"

    for code in db["pending"]:
        # This creates a clickable link that already includes the password
        response += f"""
        <p>{code} 
        <a href='/approve/{code}?password={ADMIN_PASSWORD}'>[ Approve Now ]</a>
        </p>
        """
    return response


@app.route("/approve/<code>")
def approve(code):
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        return "Unauthorized."

    db = load_db()
    if code in db["pending"]:
        db["pending"].remove(code)
        
        # Change from .append() to dictionary assignment
        # This generates the password the user needs to enter
        db["approved"][code] = generate_password() 
        
        save_db(db)
        return f"Approved successfully! Password is: {db['approved'][code]}"

    return "Code not found."

@app.route("/suggest", methods=["POST"])
def suggest():
    suggestion = request.form.get("suggestion")

    if suggestion:
        with open("suggestions.txt", "a") as f:
            f.write(suggestion + "\n")

        return "Suggestion received."
    else:
        return "No suggestion provided."
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
