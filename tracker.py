from flask import Flask, render_template, session, url_for, request, redirect, flash
from models import User
import trackerutils

app = Flask(__name__)
app.secret_key = "fdajfdjajfdkjflsdkjakdsjflajdslk"

@app.route("/", methods=["GET"])
def index():
    if "username" in session:
        return render_template("home.html", ten_most_recent_events=[{"id": "tmp", "date": "12-16-2017", "paid_for_by": "andrewhalle", "joke": "This is a test joke."}])
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        data = request.form
        if "username" not in data or "password" not in data:
            flash("Username and password required", "error")
            return redirect(url_for("login"))
        username = data["username"]
        password = data["password"]
        user = User.by_username(username)
        submitted_h = trackerutils.get_password_hash_and_salt(password, user.salt)[0]
        if submitted_h != user.password_hash:
            flash("Incorrect password", "error")
            return redirect(url_for("login"))
        session["username"] = user.username
        session["profile_picture"] = user.profile_picture or url_for("static", filename="images/unknown_profile_picture.png")
        flash("Successfully logged in!", "success")
        return redirect(url_for("index"))

@app.route("/logout", methods=["GET"])
def logout():
    del session["username"]
    flash("Successfully logged out!", "success")
    return redirect(url_for("index"))

@app.route("/users/<username>/edit", methods=['GET', 'POST'])
def edit_user(username):
    return

@app.route("/users/create", methods=["GET", "POST"])
def create_user():
    if request.method == "GET":
        return render_template("create_user.html")
    elif request.method == "POST":
        data = request.form
        if "username" not in data or "password" not in data or "confirm_password" not in data:
            flash("Username and password required", "error")
            return redirect(url_for("create_user"))
        username = data["username"]
        password = data["password"]
        confirm_password = data["confirm_password"]
        if password != confirm_password:
            flash("Password and confirmation do not match", "error")
            return redirect(url_for("create_user"))
        user = User.create(username, password)
        session["username"] = user.username
        session["profile_picture"] = user.profile_picture or url_for("static", filename="images/unknown_profile_picture.png")
        flash("Account created!", "success")
        return redirect(url_for("index"))

@app.route("/events", methods=['POST'])
def create_event():
    return

@app.route("/events/<id>/picture", methods=["GET"])
def get_event_picture(id):
    return
