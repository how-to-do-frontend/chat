from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from markupsafe import escape
from datetime import datetime, timezone
import pendulum
import requests
import json
import subprocess
import bcrypt
from flask_mysqldb import MySQL, MySQLdb
from functools import wraps

app = Flask(__name__)

app.secret_key = "IK8W1j^jiC9a3wxPVYYUa@eFvRx8@9Xzm8nPz9cBQ*t1jdEDi1"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ketochat"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)
# Protected func
def protected(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not session:
            return await render_template('login.html', msg='You must be logged in to access that page.')
        return await func(*args, **kwargs)
    return wrapper
################################################################
# Main Routes
################################################################
# Home page
@app.route("/")
def index():
    return render_template('index.html')

# Me (PROTECTED)
@app.route("/channels/@me")
@protected
def me():
    return render_template('me.html', session=session)

# Friends list (PROTECTED)
@app.route("/friends")
@protected
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
                           offlineCount=offlineCount,
                           session=session
                        )

# Settings (PROTECTED)
@app.route("/settings")
@protected
def settings():
    req2 = requests.get("http://localhost:5000/api/changelogs")
    changelogs = json.loads(req2.content)

    today = pendulum.now().to_formatted_date_string()

    gitShaHashShort = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
    gitShaHashShort = str(gitShaHashShort, "utf-8").strip()

    return render_template('settings/settings.html',
                           changelogs=changelogs,
                           today=today,
                           gitShaHashShort=gitShaHashShort,
                           session=session
                        )

# Profile Settings (PROTECTED)
@app.route("/settings/profile")
@protected
def profile():
    req2 = requests.get("http://localhost:5000/api/changelogs")
    changelogs = json.loads(req2.content)

    today = pendulum.now().to_formatted_date_string()

    gitShaHashShort = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
    gitShaHashShort = str(gitShaHashShort, "utf-8").strip()

    return render_template('settings/profile.html',
                           changelogs=changelogs,
                           today=today,
                           gitShaHashShort=gitShaHashShort,
                           session=session
                        )

# Servers (PROTECTED)
@app.route("/channels/<int:snowflake>")
@protected
def snowflake(snowflake):
    timstamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

    return f"Snowflake: {timstamp}"




################################################################
# Auth Routes
################################################################
# Logout
@app.route("/auth/logout")
@protected
def logout():
    session.clear()
    return redirect("/auth/login")

# Login
@app.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"].encode("utf-8")
        password = request.form["password"].encode("utf-8")

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode("utf-8")) == user["password"].encode("utf-8"):
                session["logged_in"] = True
                session["id"] = user["id"]
                session["username"] = user["username"]
                session["email"] = user["email"]
                session["avatar"] = user["avatar"]
                return redirect("/channels/@me")
            else:
                return render_template("login.html", msg="Invalid password...")
        else:
            return render_template("login.html", msg="User not found...")

# Register
@app.route("/auth/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form["email"].encode("utf-8")
        username = request.form["username"].encode("utf-8")
        password = request.form["password"].encode("utf-8")
        confirm_password = request.form["confirm_password"].encode("utf-8")

        cur = mysql.connection.cursor()
        if (len(username) < 3):
            return render_template("register.html", msg="Username must be 3 characters or longer...")
        if (len(password) < 6):
            return render_template("register.html", msg="Password must be 6 characters or longer...")
        if (password != confirm_password):
            return render_template("register.html", msg="Passwords do not match...")
        
        timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cur.execute("INSERT INTO users (id, username, password, email) VALUES (%s, %s, %s, %s)", (timestamp, username, hashed_password, email))
        mysql.connection.commit()
        return redirect("/auth/login")


################################################################
# API Routes
################################################################
# Get changelogs (PROTECTED)
@app.route("/api/changelogs", methods=["GET"])
@protected # TODO: why?
def get_changelogs():
    changelogs = [
        {"title": "Securing your account with 2FA"},
        {"title": "Custom Accent Color"},
    ]

    return jsonify(changelogs)

# Get current user (PROTECTED)
@app.route("/api/@me", methods=["GET"])
@protected
def get_current_user():
    if (session["logged_in"] == True):    
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (session["email"],))
        user = cur.fetchone()
        cur.close()

        return jsonify(user)
    else:
        return "You are not logged in!"

# Get friends (PROTECTED)
@app.route("/api/@me/friends", methods=["GET"])
@protected
def get_friends():
    #placeholder friends
    friends = []

    return jsonify(friends)

if __name__ == "__main__":
    app.run(debug=True)
