from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os, json



# Import your model and DB setup
import config
from models import db, User


# -------------------- App Setup --------------------
app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# -------------------- Login Manager --------------------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- Temp JSON pattern storage --------------------
DATA_FILE = "data/patterns.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -------------------- Routes --------------------

@app.route("/")
@login_required
def home():
    patterns = load_data()
    return render_template("index.html", patterns=patterns)

@app.route("/", methods=["POST"])
@login_required
def add_pattern():
    name = request.form["name"]
    threads = request.form["threads"].split(",")
    patterns = load_data()
    patterns.append({
        "name": name,
        "threads": [t.strip() for t in threads]
    })
    save_data(patterns)
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("That username is already taken.")
            return redirect("/register")

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can now log in.")
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")
        flash("Invalid username or password.")
        return redirect("/login")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/floss", methods=["GET", "POST"])
@login_required
def floss():
    if request.method == "POST":
        code = request.form["code"]
        length = float(request.form.get("length", 8.7))
        # Save to DB or list (optional placeholder here)
        flash("Floss added.")
    flosses = []  # Replace with actual data
    return render_template("floss.html", flosses=flosses)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # Handle uploaded PDF
        pdf_file = request.files.get("pdf")
        if pdf_file:
            flash("File uploaded successfully.")
        else:
            flash("Please select a file.")
    return render_template("upload.html")


@app.route("/stitchable")
@login_required
def stitchable():
    stitchable_patterns = []  # Replace with logic based on available floss
    return render_template("stitchable.html", stitchable=stitchable_patterns)


# -------------------- App Launch --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001, debug=True)
