from flask import Flask, render_template, session, url_for, request, redirect, flash, send_file
from models import User, Event
import trackerutils
import boto3
import io

app = Flask(__name__)
app.secret_key = "fdajfdjajfdkjflsdkjakdsjflajdslk"

@app.route("/", methods=["GET"])
def index():
    if "username" in session:
        return render_template("home.html", events=Event.get_all_events())
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
        session["phone_number"] = user.phone_number
        flash("Successfully logged in!", "success")
        return redirect(url_for("index"))

@app.route("/logout", methods=["GET"])
def logout():
    del session["username"]
    flash("Successfully logged out!", "success")
    return redirect(url_for("index"))

@app.route("/users/<username>/edit", methods=['GET', 'POST'])
def edit_user(username):
    if username != session["username"]:
        flash("You can't edit someone else's account!", "error")
        return redirect(url_for("index"))
    if request.method == "GET":
        curr_user = User.by_username(session["username"])
        return render_template("edit_user.html", user=curr_user)
    elif request.method == "POST":
        data = request.form
        user = User.by_username(session["username"])
        user.name = data["name"]
        user.phone_number = data["phone"]
        user.save()

        profile_picture = request.files["profile_picture"]
        if profile_picture:
            # upload to S3
            s3 = boto3.resource("s3", region_name="us-west-1")
            bucket = s3.Bucket("cheesy-stick-tracker-images")
            bucket.put_object(Key="profile_pictures/profile-" + username + ".jpeg", Body=profile_picture)
            
        flash("Successfully updated!", "success")
        return redirect(url_for("edit_user", username=session["username"]))

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
            return redirect(url_for("create_user", username=session["username"]))
        user = User.create(username, password)
        session["username"] = user.username
        flash("Account created!", "success")
        return redirect(url_for("index"))

@app.route("/events/create", methods=['GET', 'POST'])
def create_event():
    if request.method == "GET":
        names = User.get_all_names()
        return render_template("create_event.html", names=names)
    else:
        data = request.form
        date = data["date"]
        paid_for_by = data["paid_for_by"]
        event = Event.create(date, paid_for_by)
        flash("Added cheesy stick even!", "success")
        return redirect(url_for("index"))

@app.route("/events/<id>/picture", methods=["GET"])
def get_event_picture(id):
    return

@app.route("/users/<username>/profile_picture", methods=["GET"])
def get_profile_picture(username):
    s3 = boto3.resource("s3", region_name="us-west-1")
    bucket = s3.Bucket("cheesy-stick-tracker-images")
    object = bucket.Object("profile_pictures/profile-" + username + ".jpeg")
    file_stream = io.BytesIO()
    object.download_fileobj(file_stream)
    file_stream.seek(0)
    return send_file(file_stream, mimetype="image/jpg", cache_timeout=0)
