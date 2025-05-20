from flask import Flask, request, jsonify, render_template, send_file, url_for, send_from_directory
import csv
from flask import Response
from flask_cors import CORS
import os, jsonschema_specifications
from dotenv import load_dotenv
import json



app = Flask(__name__)
CSV_PATH = "user_responses.csv"
CORS(app)
# Load model once globally






BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "source files")
USER_STATE_FILE = os.path.join(BASE_DIR, "user_data.json")
USER_LOG_DIR = os.path.join(BASE_DIR, "user_logs")

# Ensure directories and user data storage exist
os.makedirs(USER_LOG_DIR, exist_ok=True)
if not os.path.exists(USER_STATE_FILE):
    with open(USER_STATE_FILE, "w") as f:
        json.dump({}, f)

@app.route("/get_user_data", methods=["POST"])
def get_user_data():
    user_id = request.json["user_id"]
    with open(USER_STATE_FILE) as f:
        state = json.load(f)
    
    if user_id not in state:
        return jsonify({"error": "User ID not found"}), 403
    
    return jsonify(state[user_id])


@app.route("/get_csv/<filename>")
def get_csv(filename):
    return send_from_directory(DATA_DIR, filename)

@app.route("/save", methods=["POST"])
def save():
    data = request.json
    user_id = data["user_id"]
    index = data["index"]
    ranking = data["ranking"]
    translations = data.get("translations", {})

    log_file = os.path.join(USER_LOG_DIR, f"{user_id}.csv")
    is_new = not os.path.exists(log_file)

    with open(log_file, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["index", "ranking", "maats", "zero_shot", "single_agent"])
        writer.writerow([
            index,
            ",".join(ranking),
            translations.get("maats", ""),
            translations.get("zero_shot", ""),
            translations.get("single_agent", "")
        ])

    # Update user progress
    with open(USER_STATE_FILE) as f:
        state = json.load(f)
    state[user_id]["index"] = index + 1
    with open(USER_STATE_FILE, "w") as f:
        json.dump(state, f)

    return {"status": "saved"}


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)
