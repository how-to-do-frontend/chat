from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from markupsafe import escape
from datetime import datetime, timezone
import pendulum
import requests
import json
import subprocess

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

# Me (PROTECTED)
@app.route("/channels/@me")
def me():
    return render_template('me.html')

# Friends list (PROTECTED)
@app.route("/friends")
def friends():
    req = requests.get("http://localhost:5000/api/@me/friends")
    friends = json.loads(req.content)

    onlineCount = 0
    offlineCount = 0
    for i in range(0, len(friends)):
        if friends[i]["status"] == "Online":
            onlineCount += 1
        else:
            offlineCount += 1
    
    return render_template('friends.html',
                           friends=friends,
                           onlineCount=onlineCount,
                           offlineCount=offlineCount
                        )

# Settings (PROTECTED)
@app.route("/settings")
def settings():
    req = requests.get("http://localhost:5000/api/@me")
    me = json.loads(req.content)

    req2 = requests.get("http://localhost:5000/api/changelogs")
    changelogs = json.loads(req2.content)

    today = pendulum.now().to_formatted_date_string()

    gitShaHashShort = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
    gitShaHashShort = str(gitShaHashShort, "utf-8").strip()

    return render_template('settings/settings.html',
                           me=me,
                           changelogs=changelogs,
                           today=today,
                           gitShaHashShort=gitShaHashShort
                        )

# Profile Settings (PROTECTED)
@app.route("/settings/profile")
def profile():
    req = requests.get("http://localhost:5000/api/@me")
    me = json.loads(req.content)

    req2 = requests.get("http://localhost:5000/api/changelogs")
    changelogs = json.loads(req2.content)

    today = pendulum.now().to_formatted_date_string()

    return render_template('settings/profile.html',
                           me=me,
                           changelogs=changelogs,
                           today=today
                        )

# Servers (PROTECTED)
@app.route("/channels/<int:snowflake>")
def snowflake(snowflake):
    timstamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

    return f"Snowflake: {timstamp}"




################################################################
# API Routes
################################################################
# Get changelogs (PROTECTED)
@app.route("/api/changelogs", methods=["GET"])
def get_changelogs():
    changelogs = [
        {"title": "Securing your account with 2FA"},
        {"title": "Custom Accent Color"},
    ]

    return jsonify(changelogs)

# Get current user (PROTECTED)
@app.route("/api/@me", methods=["GET"])
def get_current_user():
    #placeholder user
    current_user = [
        {"id": 459738097622712320, "avatar": "https://cdn.discordapp.com/avatars/459738097622712320/a_a3094d93bbc01dd74140e768abc59203.gif?size=4096", "username": "ophx", "customStatus": "", "status": "Online", "userType": "user", "badges": ["Staff", "Bug Hunter", "Early User", "Supporter"]}
    ]

    return jsonify(current_user)

# Get friends (PROTECTED)
@app.route("/api/@me/friends", methods=["GET"])
def get_friends():
    #placeholder friends
    friends = [
        {"id": 1685391664700, "avatar": "https://cdn.discordapp.com/avatars/659022591071223819/48c9606a28a3ef1d284aa1b7c0914be9.png?size=4096", "username": "Iriel", "customStatus": "https://feds.lol/068", "status": "Online"},
        {"id": 1685392169569, "avatar": "https://cdn.discordapp.com/avatars/915795771268419604/edb5ef4d0307bf8a0a943e60cd81befd.png?size=4096", "username": "sadnesswillsear", "customStatus": "😭 why is Rising of the Shield Hero such a good anime what the fuck", "status": "Online"},
        {"id": 1096249933994139729, "avatar": "https://cdn.discordapp.com/avatars/1096249933994139729/804bd9313e35166f99430a5a2b4e0e8f.png?size=4096", "username": "tree", "customStatus": "\"Life is like a penis, sometimes it's up and sometimes it's down, but it never stays hard forever\" - George Washington", "status": "Online"},
    ]

    return jsonify(friends)

if __name__ == "__main__":
    app.run(debug=True)