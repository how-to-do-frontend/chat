from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import escape
from datetime import datetime, timezone 

app = Flask(__name__)

# Home page
@app.route("/")
def index():
    return render_template('index.html')

# Me
@app.route("/channels/@me")
def me():
    return render_template('me.html')

# Other users
@app.route("/channels/<int:snowflake>")
def snowflake(snowflake):
    timstamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    return f"Snowflake: {timstamp}"

if __name__ == "__main__":
    app.run(debug=True)