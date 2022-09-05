import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from helpers import login_required, isadmin, admin_required, mail_check

app = Flask(__name__)

app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["SECRET_KEY"] = "my_precious"

mail = Mail(app)
secret = URLSafeTimedSerializer(app.config["SECRET_KEY"])

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    dataset = []
    
    rows = db.execute("SELECT * FROM sessions WHERE week = (SELECT MAX(week) FROM sessions)")
    for row in rows:
        locked_registered = False
        locked_attended = -1

        if db.execute("SELECT * FROM registrants WHERE userID = ? and sessionID = ?", session["user_id"], row["id"]):
            locked_registered = True

        on_attendance = db.execute("SELECT * FROM attendance WHERE sessionID = ?", row["id"])
        off_attendance = db.execute("SELECT * FROM attendance WHERE sessionID = ? AND userID = ?", row["id"], -1)

        if off_attendance:
            locked_attended = 0

        elif on_attendance:
            locked_attended = len(on_attendance)

        dic = {
            "week": row["week"],
            "name": row["name"],
            "time": row["time"],
            "registered": locked_registered,
            "attended": locked_attended,
            "id": row["id"]
        }
        dataset.append(dic)

    if request.method == "GET":
        return render_template("index.html", dataset = dataset)

    else:
        db.execute("INSERT INTO registrants (userID, sessionID) VALUES(?, ?)", session["user_id"], request.form["register"])
        return redirect("/")


@app.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add():
    if request.method == "GET":
        return render_template("add.html")

    else:
        if not request.form.get("week") or not request.form.get("name") or not request.form.get("time"):
            return render_template("add.html", error_message = "At least 1 input missing, error code: 400")

        db.execute("INSERT INTO sessions (week, name, time) VALUES(?, ?, ?)", request.form.get("week"), request.form.get("name"), request.form.get("time"))
        return redirect("/")


@app.route("/delete", methods=["GET", "POST"])
@login_required
@admin_required
def delete():
    rows = db.execute("SELECT * FROM sessions")
    if request.method == "GET":
        return render_template("delete.html", rows = rows)

    else:
        if not request.form.get("id"):
            return render_template("delete.html", error_message = "At least 1 input missing, error code: 400")

        try:
            int(request.form.get("id"))

        except ValueError:
            return render_template("delete.html", error_message = "Input should be positive integer, error code: 400")

        db.execute("DELETE FROM sessions WHERE id = ?", request.form.get("id"))
        db.execute("DELETE FROM registrants WHERE sessionID = ?", request.form.get("id"))
        db.execute("DELETE FROM attendance WHERE sessionID = ?", request.form.get("id"))
        return redirect("/")

@app.route("/registered")
@login_required
def registered():
    dataset = db.execute("SELECT sessions.week, sessions.name, sessions.time FROM sessions INNER JOIN registrants on sessions.id = registrants.sessionID WHERE registrants.userID = ?", session["user_id"])
    return render_template("registered.html", dataset = dataset)


@app.route("/attendance", methods=["GET", "POST"])
@login_required
@admin_required
def attendance():
    if request.method == "POST":
        if "attendance" in request.form:
            people = db.execute("SELECT users.mail, users.id FROM users INNER JOIN registrants on users.id = registrants.userID WHERE registrants.sessionID = ?", request.form["attendance"])
            session["picked_session"] = request.form["attendance"]
            return render_template("attendance.html", people = people)

        else:
            attending = request.form.getlist("present")
            print(attending)
            for attendee in attending:
                db.execute("INSERT INTO attendance (userID, sessionID) VALUES(?, ?)", attendee, session["picked_session"])

            if not attending:
                db.execute("INSERT INTO attendance (userID, sessionID) VALUES(?, ?)", -1, session["picked_session"])

            return redirect("/")
    else:
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    else:
        if not request.form.get("mail") or not request.form.get("password"):
            return render_template("login.html", error_message = "At least 1 credential missing, error code: 400")

        rows = db.execute("SELECT * FROM users WHERE mail = ?", request.form.get("mail"))
        if len(rows) != 1:
            return render_template("login.html", error_message = "You are not registered, error code: 400")

        if check_password_hash(rows[0]["password"], request.form.get("password")):
            if(db.execute("SELECT verified FROM users WHERE mail = ?", request.form.get("mail"))[0]["verified"] != "false"):
                session["user_id"] = rows[0]["id"]

            if isadmin(request.form.get("mail")):
                session["moderator"] = 1

            return redirect("/")

        return render_template("login.html", error_message = "Invalid password, error code: 400")


@app.route("/register", methods=["GET", "POST"])
def register():
    print(os.environ.get("MAIL_DEFAULT_SENDER"))
    if request.method == "GET":
        return render_template("register.html")

    else:
        email = request.form.get("mail")
        session["mail"] = email
        validation = request.form.get("validation")
        hashed = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        if not email or not validation:
            return render_template("register.html", error_message = "At least 1 credential missing, code: 400")

        if not mail_check(email):
            return render_template("register.html", error_message = "Make sure that entered mail belongs to Sabanci University, code: 400")

        if request.form.get("password") != validation:
            return render_template("register.html", error_message = "Passwords do not match, code: 400")

        already_exists = db.execute("SELECT * FROM users WHERE mail = ?", request.form.get("mail"))
        if already_exists:
            return render_template("register.html", error_message = "User already registered, code: 400")

        db.execute("INSERT INTO users (mail, password, verified) VALUES(?, ?, ?)", email, hashed, "false")

        token = secret.dumps(email, salt = "verification")

        msg = Message("Mail Validation", sender = os.getenv("MAIL_DEFAULT_SENDER"), recipients = [email])

        link = url_for("mail_validation", token = token, _external = True)
        msg.body = link
        mail.send(msg)

        try:
            mail.send(msg)
            return render_template("verification.html", email = email)

        except smtplib.SMTPConnectionError:
            db.execute("DELETE FROM users WHERE mail = ?", email)
            return render_template("register.html", error_message = "Invalid email input, error code: 400")


@app.route("/mail_validation/<token>")
def mail_validation(token):
    try:
        email = secret.loads(token, salt = "verification", max_age = 30)

    except SignatureExpired:
        return render_template("login.html", error_message = "Mail time expired, register again code: 400")

    db.execute("UPDATE users SET verified = ? WHERE mail = ?", "true", email)
    return render_template("login.html", confirmation = "You have successfully completed the registration!")


@app.route("/verification")
def verification():
    return render_template("verification.html")


@app.route("/lists", methods=["GET", "POST"])
def lists():
    ID = request.form.get("attendanceList")
    print(ID)
    rows = db.execute("SELECT users.mail FROM users INNER JOIN attendance on users.id = attendance.userID WHERE attendance.sessionID = ?", ID)
    return render_template("lists.html", rows = rows)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/faq")
@login_required
def faq():
    return render_template("faq.html")

