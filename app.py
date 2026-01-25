import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "secret123"

# -----------------------------
# Persistent storage setup
# -----------------------------
DATA_DIR = "data"
POSTS_FILE = os.path.join(DATA_DIR, "posts.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)

# Load users
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Load posts
if os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, "r") as f:
        posts = json.load(f)
else:
    posts = []

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("User already exists")
            return redirect(url_for("register"))

        users[username] = password

        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.get(username) == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/create", methods=["GET", "POST"])
def create_post():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        posts.append({
            "author": session["user"],
            "title": request.form["title"],
            "content": request.form["content"]
        })

        with open(POSTS_FILE, "w") as f:
            json.dump(posts, f, indent=2)

        return redirect(url_for("index"))

    return render_template("create_post.html")

# -----------------------------
# App start
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
