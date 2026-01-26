import json
import os
import logging
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.secret_key = "super-secret-key-change-this"

csrf = CSRFProtect(app)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=1800
)

logging.basicConfig(level=logging.INFO)

# -----------------------------
# Persistent storage setup
# -----------------------------
DATA_DIR = "data"
POSTS_FILE = os.path.join(DATA_DIR, "posts.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

if os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, "r") as f:
        posts = json.load(f)
else:
    posts = []

# -----------------------------
# Security Helpers
# -----------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self';"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Server"] = ""
    return response

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            flash("All fields required")
            return redirect(url_for("register"))

        if username in users:
            flash("User already exists")
            return redirect(url_for("register"))

        users[username] = generate_password_hash(password)

        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        stored_hash = users.get(username)

        if stored_hash and check_password_hash(stored_hash, password):
            session.clear()
            session["user"] = username
            session.permanent = True
            logging.info(f"User logged in: {username}")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if len(title) < 3 or len(content) < 5:
            flash("Post too short")
            return redirect(url_for("create_post"))

        posts.append({
            "author": session["user"],
            "title": title,
            "content": content
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
