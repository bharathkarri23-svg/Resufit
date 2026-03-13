from flask import Flask, session, render_template, request, redirect, url_for,jsonify
import sqlite3
import secrets
import re
from werkzeug.security import generate_password_hash, check_password_hash
from google_auth_oauthlib.flow import Flow
import requests
import os
import random
import time
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_SECRETS_FILE = os.getenv("client_secret")

SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

REDIRECT_URI = os.getenv("redirect_uri") 

# Strong secret key
app.secret_key = os.getenv("secret_key")

DATABASE = "database.db"

# -------------------------------
# Create Database & Table
# -------------------------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT,
            provider TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------------
# Home Page
# -------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------
# Sign Up
# -------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):
            return render_template("signup.html", error="Invalid email format")

        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(password_pattern, password):
            return render_template(
                "signup.html",
                error="Password must be at least 8 characters long and include uppercase, lowercase, number, and special character"
            )
        # Hash password
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (email, password, provider) VALUES (?, ?, ?)",
                (email, hashed_password, "signup")
            )
            conn.commit()

            return redirect(url_for("signin"))

        except sqlite3.IntegrityError:
            return render_template("signup.html", error="Email already exists")

        finally:
            conn.close()

    return render_template("signup.html")


# -------------------------------
# Sign In
# -------------------------------

@app.route("/signin", methods=["GET", "POST"])
def signin():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            session["user"] = email
            return redirect(url_for("home"))

        else:
            return render_template("signin.html", error="Invalid email or password")

    return render_template("signin.html")


# -------------------------------
# Forgot Password
# -------------------------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"].strip()
        
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):
            return render_template("forgot-password.html", error="Invalid email format")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user:
            otp = random.randint(100000, 999999)
            session["reset_email"] = email
            session["otp"] = str(otp)
            session["otp_time"] = time.time()
            session["resend_count"] = 0
            send_otp(email, otp)
            return redirect(url_for("verify"))


        else:
            return render_template("forgot-password.html", error="Email not found")

    return render_template("forgot-password.html")

# -------------------------------
# OTP Email Sender
# -------------------------------

def send_otp(to_email, otp):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    print("DEBUG EMAIL:", sender_email)
    print("DEBUG PASS:", sender_password)

    msg = MIMEText(f"Your OTP for password reset is: {otp}")
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = sender_email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        user_otp = request.form["otp"]

        if time.time() - session.get("otp_time", 0) > 300:
            return render_template("verify.html", error="OTP Expired")

        if user_otp == session.get("otp"):
            return render_template("new-pass.html", email=session.get("reset_email"))
        else:
            return render_template("verify.html", error="Invalid OTP")

    return render_template("verify.html")

# -------------------------------
# Resend OTP Route
# -------------------------------

@app.route("/resend_otp")
def resend_otp():

    if "reset_email" not in session:
        return redirect(url_for("forgot-password"))

    # Limit resend attempts
    if session.get("resend_count", 0) >= 3:
        return "Maximum resend attempts reached."

    # Prevent resend before 30 seconds
    if time.time() - session.get("otp_time", 0) < 30:
        return "Please wait before requesting again."

    email = session["reset_email"]
    otp = random.randint(100000, 999999)

    session["otp"] = str(otp)
    session["otp_time"] = time.time()
    session["resend_count"] += 1

    send_otp(email, otp)

    return redirect(url_for("verify"))

# -------------------------------
# New Password
# -------------------------------

@app.route("/new-pass", methods=["POST"])
def new_pass():
    if "reset_email" not in session:
        return redirect(url_for("forgotpass"))

    email = session.get("reset_email")

    new_password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"

    if new_password != confirm_password:
        return render_template(
            "new-pass.html",
            email=email,
            error="Passwords do not match"
        )

    if not re.match(password_pattern, new_password):
        return render_template(
            "new-pass.html",
            email=email,
            error="Password must be at least 8 characters long and include uppercase, lowercase, number, and special character"
            )

    if email:

        hashed_password = generate_password_hash(new_password)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (hashed_password, email)
        )

        conn.commit()
        conn.close()

        session.pop("reset_email", None)

        session["user"] = email
        return redirect(url_for("home"))

    else:
        return redirect(url_for("forgot_password"),email=email)


@app.route("/google-login")
def google_login():

    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    # Save state
    session["state"] = state

    # Save PKCE code verifier
    session["code_verifier"] = flow.code_verifier

    return redirect(authorization_url)


@app.route("/callback")
def callback():


    if "error" in request.args:
        return render_template("signin.html", error="Google authentication failed")

    state = session.get("state")

    if not state:
        return redirect(url_for("signin"))

    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=session["state"],
        redirect_uri=REDIRECT_URI
    )

    # Restore PKCE code verifier
    flow.code_verifier = session["code_verifier"]

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"access_token": credentials.token}
    )

    user_info = response.json()

    email = user_info["email"]

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("""
            INSERT INTO users (email, password, provider)
            VALUES (?, ?, ?)
        """, (email,"", "google"))
        conn.commit()

        session["reset_email"] = email
        conn.close()
        return render_template("new-pass.html",email = email)

    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()

    if row is None or row[0] is None:
        session["reset_email"] = email
        conn.close()
        return render_template("new-pass.html",email = email)

    conn.close()

    session["user"] = email
    session["provider"] = "google"

    return redirect(url_for("home"))


# -------------------------------
# Protected Home
# -------------------------------

@app.route("/home")
def home():

    if "user" not in session:
        return redirect(url_for("signin"))

    return render_template("home.html", email=session["user"])


# -------------------------------
# Logout
# -------------------------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("index"))


# -------------------------------
# Run App
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)