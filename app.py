from flask import Flask, request, render_template, jsonify, send_file
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB = "users.db"
TXT = "users.txt"


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            source TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_txt(uid, name, source, created_at):
    new_file = not os.path.exists(TXT)

    with open(TXT, "a", encoding="utf-8") as f:
        if new_file:
            f.write("UID | In-Game Name | Source | Date\n")
            f.write("-" * 70 + "\n")

        f.write(f"{uid} | {name} | {source} | {created_at}\n")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True) or request.form

    uid = str(data.get("uid", "")).strip()
    name = str(data.get("name", "")).strip()
    source = str(data.get("source", "")).strip()

    if not uid or not name:
        return jsonify({
            "success": False,
            "message": "UID aur In-Game Name dono required hain."
        }), 400

    # Basic validation
    if len(uid) > 30:
        return jsonify({
            "success": False,
            "message": "Invalid UID."
        }), 400

    if len(name) > 50:
        return jsonify({
            "success": False,
            "message": "In-Game Name bahut lamba hai."
        }), 400

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB)

    try:
        conn.execute(
            "INSERT INTO users (uid, name, source, created_at) VALUES (?, ?, ?, ?)",
            (uid, name, source, now)
        )
        conn.commit()

        save_txt(uid, name, source, now)

        return jsonify({
            "success": True,
            "message": "Data successfully submit ho gaya."
        })

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "message": "Ye UID pehle hi submit ho chuka hai."
        }), 409

    finally:
        conn.close()


@app.route("/download")
def download():
    if not os.path.exists(TXT):
        return "Abhi koi data available nahi hai.", 404

    return send_file(
        TXT,
        as_attachment=True,
        download_name="users.txt"
    )


if __name__ == "__main__":
    init_db()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )