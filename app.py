from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, json, uuid

# Import config and model definitions
import config
from models import db, User, Pattern

# -------------------- App Setup --------------------
app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# Ensure UPLOAD_FOLDER is set
if not app.config.get("UPLOAD_FOLDER"):
    raise ValueError("UPLOAD_FOLDER is not set in the configuration.")

# -------------------- Login Manager --------------------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- JSON File Storage --------------------
DATA_FILE = "data/patterns.json"
FLOSS_FILE = "data/floss.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_floss():
    if os.path.exists(FLOSS_FILE):
        with open(FLOSS_FILE) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_floss(flosses):
    with open(FLOSS_FILE, "w") as f:
        json.dump(flosses, f, indent=2)

def get_floss_inventory():
    flosses = load_floss()
    return [floss["code"] for floss in flosses]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# -------------------- Routes --------------------

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    patterns = load_data()
    db_patterns = Pattern.query.filter_by(user_id=current_user.id).all()

    # Add decoded floss_data as an attribute to each pattern
    for pattern in db_patterns:
        try:
            pattern._floss_data = json.loads(pattern.floss_codes or "[]")
        except json.JSONDecodeError:
            pattern._floss_data = []

    return render_template("index.html", db_patterns=db_patterns)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("That username is already taken.")
            return redirect("/register")

        new_user = User(
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created!")
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

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        name = request.form.get("name")
        floss_data_raw = request.form.get("floss_data")
        floss_data = json.loads(floss_data_raw) if floss_data_raw else []

        file = request.files.get("image")

        # validation
        if not name:
            flash("Missing pattern name.", "error")
            return redirect("/upload")

        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash("Invalid file type. Please upload an image or PDF.", "error")
            return redirect("/upload")

        # Save to database
        new_pattern = Pattern(
            name=name,
            floss_codes=json.dumps(floss_data),
            floss_yardage="",
            image_filename=filename,
            user_id=current_user.id
        )
        db.session.add(new_pattern)
        db.session.commit()

        # Save to patterns.json
        patterns = load_data()
        patterns.append({
            "name": name,
            "floss_data": floss_data,
            "image_filename": filename,
            "user_id": current_user.id
        })
        save_data(patterns)

        flash("Pattern uploaded successfully.", "success")
        return redirect("/")
    return render_template("upload.html")

@app.route("/floss", methods=["GET", "POST"])
@login_required
def floss():
    flosses = load_floss()
    if request.method == "POST":
        code = request.form["code"].strip()
        length = float(request.form.get("length", 8.7))
        flosses.append({"code": code, "length": length})
        save_floss(flosses)
        flash("Floss added.")
        return redirect("/floss")

    return render_template("floss.html", flosses=flosses)

@app.route("/delete/<int:pattern_id>", methods=["POST"])
@login_required
def delete_pattern(pattern_id):
    pattern = Pattern.query.filter_by(id=pattern_id, user_id=current_user.id).first()
    if not pattern:
        flash("Pattern not found.")
        return redirect("/")

    # Remove file from disk if it exists
    if pattern.image_filename:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], pattern.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(pattern)
    db.session.commit()
    flash("Pattern deleted.")
    return redirect("/")

    
@app.route("/floss/edit_delete", methods=["POST"])
@login_required
def edit_or_delete_floss():
    code = request.form["code"]
    action = request.form["action"]
    flosses = load_floss()

    if action == "delete":
        flosses = [f for f in flosses if f["code"] != code]
        flash(f"Deleted floss {code}.", "success")

    elif action == "update":
        delta = request.form.get("new_length", "")
        try:
            delta = float(delta)
            for f in flosses:
                if f["code"] == code:
                    f["length"] += delta
                    flash(f"Updated floss {code} by {delta:+}. New total: {f['length']} yards.", "success")
                    break
        except ValueError:
            flash("Invalid number entered.", "error")

    save_floss(flosses)
    return redirect("/floss")


@app.route("/stitchable")
@login_required
def stitchable():
    patterns = Pattern.query.all()
    inventory = get_floss_inventory()

    matchable = []
    for pattern in patterns:
        try:
            floss_list = json.loads(pattern.floss_codes or "[]")
            floss_codes = [f["code"] for f in floss_list]
            if all(code in inventory for code in floss_codes):
                matchable.append(pattern)
        except Exception:
            continue

    return render_template("stitchable.html", stitchable=matchable)

# -------------------- Launch --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001, debug=True)