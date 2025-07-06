from flask import Flask, request, render_template, redirect
import json, os


app = Flask(__name__)
DATA_FILE = "data/patterns.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    patterns = load_data()
    if request.method == "POST":
        name = request.form["name"]
        threads = request.form["threads"].split(",")
        patterns.append({"name": name, "threads": [t.strip() for t in threads]})
        save_data(patterns)
        return redirect("/")
    return render_template("index.html", patterns=patterns)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
