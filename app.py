from flask import Flask, request, render_template, jsonify
from supabase import create_client, Client
from datetime import datetime
import os

app = Flask(__name__)

# Render Environment Variables से Supabase URL और API Key लें
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Supabase Client Initialize करें
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("Warning: SUPABASE_URL ya SUPABASE_KEY missing hai!")


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
        return jsonify({"success": False, "message": "UID aur In-Game Name dono required hain."}), 400

    if len(uid) > 30:
        return jsonify({"success": False, "message": "Invalid UID."}), 400

    if len(name) > 50:
        return jsonify({"success": False, "message": "In-Game Name bahut lamba hai."}), 400

    try:
        # Supabase के 'users' टेबल में डेटा इन्सर्ट करें
        # ध्यान दें: Supabase में 'name' नाम का कॉलम होना ज़रूरी है (जो हमने पहले बात की थी)
        response = supabase.table("users").insert({
            "uid": uid,
            "name": name,
            "source": source
        }).execute()

        # अगर Supabase से डेटा आ गया, मतलब इन्सर्ट हो गया
        if response.data:
            return jsonify({"success": True, "message": "Data successfully submit ho gaya."})
        
    except Exception as e:
        error_msg = str(e)
        # अगर UID पहले से है (Unique Constraint Error)
        if "duplicate key value" in error_msg.lower() or "unique" in error_msg.lower():
            return jsonify({"success": False, "message": "Ye UID pehle hi submit ho chuka hai."}), 409
        
        # कोई और एरर
        return jsonify({"success": False, "message": f"Database error: {error_msg}"}), 500

    return jsonify({"success": False, "message": "Kuch galat ho gaya."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
