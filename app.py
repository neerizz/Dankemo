from flask import Flask, flash, render_template, request, redirect, session
from cs50 import SQL
from tempfile import mkdtemp
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///maindb.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")



@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    
    if not request.form.get("username"):
        flash("Please provide a username")
        return redirect("/login")

    elif not request.form.get("password"):
        flash("Kindly enter a password")
        return redirect("/login")

    rows = db.execute("SELECT * FROM users WHERE username = :username",
                        username=request.form.get("username"))
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        flash("Invalid username and/or password!")
        return redirect("/login")
    session["user_id"] = rows[0]["id"]
    flash("You have successfully logged in.")
    return redirect("/home")



@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if not request.form.get("username"):
        flash("Username field is blank!")
        return redirect("/register")

    elif not request.form.get("password"):
        flash("Password field is blank!")
        return redirect("/register")

    elif request.form.get("password") != request.form.get("confirmpass"):
        flash("Passwords do not match!")
        return redirect("/register")
    else:
        hashpwd = generate_password_hash(request.form.get("password"))
        musrs = db.execute("SELECT * FROM users WHERE username=:username",
                             username=request.form.get("username"))
        if len(musrs) != 0:
            flash("Username not available!")
            return redirect("/register")
        resp = db.execute("INSERT INTO users(username, time, hash, gpoints) VALUES(:username, :time, :hash, :gpoints)", username=request.form.get("username"), time=request.form.get("time"), hash=hashpwd, gpoints=0)
        session["user_id"] = resp
        return redirect("/home")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have successfully logged out.")
    return redirect("/login")


@app.route("/home")
@login_required
def home():
    uname = db.execute("SELECT username FROM users WHERE id=:cid", 
                    cid=session["user_id"])[0]["username"]
    gpoints = db.execute("SELECT gpoints FROM users WHERE id=:cid", 
                cid=session["user_id"])[0]["gpoints"]
    time = db.execute("SELECT time FROM users WHERE id=:cid", 
                cid=session["user_id"])[0]["time"]
    entries = db.execute("SELECT * FROM journals WHERE username=:username", 
                username=uname)
    return render_template("home.html", uname=uname, gpoints=gpoints, time=time, entries=entries)


@app.route("/add", methods = ["GET", "POST"])
@login_required
def add():
    if request.method == "GET":
        uname = db.execute("SELECT username FROM users WHERE id=:cid", 
                    cid=session["user_id"])[0]["username"]
        return render_template("add_note.html", uname=uname)
    else:
        title = request.form.get("title")
        note = request.form.get("note_detailed")
        uname = db.execute("SELECT username FROM users WHERE id=:cid", 
                cid=session["user_id"])[0]["username"]
        cgpoints = db.execute("SELECT gpoints FROM users WHERE id=:cid", 
                cid=session["user_id"])[0]["gpoints"]
        ngpoints=cgpoints+1
        db.execute("UPDATE users SET gpoints = :gpoints WHERE id = :cid",
            gpoints=ngpoints, cid=session["user_id"])
        db.execute("INSERT INTO journals(username, date, note, title) VALUES(:username, current_date, :note, :title)", username=uname, note=note, title=title)
        return redirect("/home")

@app.route("/notes")
@login_required
def notes():
    uname = db.execute("SELECT username FROM users WHERE id=:cid", 
                    cid=session["user_id"])[0]["username"]
    entries = db.execute("SELECT * FROM journals WHERE username=:username", 
                username=uname)
    return render_template("all_notes.html", uname=uname, entries=entries)


if __name__ == '__main__':
    app.run()