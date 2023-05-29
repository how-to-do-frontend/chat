from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from markupsafe import escape
from datetime import datetime, timezone
import requests
import json

app = Flask(__name__)

################################################################
# Main Routes
################################################################
# Home page
@app.route("/")
def index():
    return render_template('index.html')

# Login
@app.route("/login")
def login():
    return "login"

# Register
@app.route("/register")
def register():
    return "register"

# Me
@app.route("/channels/@me")
def me():
    return render_template('me.html')

# Friends list
@app.route("/friends")
def friends():
    req = requests.get("http://localhost:5000/api/@me/friends")
    friends = json.loads(req.content)

    return render_template('friends.html',
                           friends=friends
                        )

# Other users
@app.route("/channels/<int:snowflake>")
def snowflake(snowflake):
    timstamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

    return f"Snowflake: {timstamp}"




################################################################
# API Routes
################################################################
# Get current user
@app.route("/api/@me", methods=["GET"])
def get_current_user():
    #placeholder user
    current_user = [
        {"id": 459738097622712320, "avatar": "https://cdn.discordapp.com/avatars/459738097622712320/a_a3094d93bbc01dd74140e768abc59203.gif?size=4096", "username": "ophx", "status": "Online", "userType": "user", "badges": ["Staff", "Bug Hunter", "Early User"]}
    ]

    return jsonify(current_user)

# Get friends
@app.route("/api/@me/friends", methods=["GET"])
def get_friends():
    #placeholder friends
    friends = [
        {"id": 1685391664700, "avatar": "", "username": "test user 1", "status": "Online"},
        {"id": 1685392169569, "avatar": "", "username": "test user 2", "status": "Offline"},
        {"id": 1685392174760, "avatar": "", "username": "test user 3", "status": "Offline"},
    ]

    return jsonify(friends)

if __name__ == "__main__":
    app.run(debug=True)