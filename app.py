from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import joblib
import numpy as np
from db import get_db_connection
from gamification import gamification_bp

# App Initialization
app = Flask(__name__)
CORS(app)
app.register_blueprint(gamification_bp, url_prefix="/gamification")

# Load model and scaler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "credit_score_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")

model = scaler = None
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ Model & Scaler Loaded Successfully")
except Exception as e:
    print("❌ Model loading failed:", e)

# Violation weights
violation_weights = {
    "overspeeding": [1, 0, 0, 0],
    "signal_jumping": [0, 1, 0, 0],
    "no_helmet_seatbelt": [0, 0, 1, 0],
    "drunk_driving": [1, 1, 1, 1],
    "triple_riding": [0, 0, 1, 0],
    "no_violation_month": [-0.5, -0.5, -0.5, -0.5],
    "fine_paid_on_time": [-0.2, -0.2, -0.2, -0.2]
}

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register_vehicle", methods=["POST"])
def register_vehicle():
    data = request.get_json()
    vehicle_number = data.get("vehicle_number")
    owner_name = data.get("owner_name")
    if not vehicle_number or not owner_name:
        return jsonify({"message": "❌ Vehicle number and owner name required"}), 400
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vehicles (vehicle_number, owner_name) VALUES (%s, %s)", (vehicle_number, owner_name))
            cursor.execute("INSERT INTO violations (vehicle_number) VALUES (%s)", (vehicle_number,))
            conn.commit()
            return jsonify({"message": "✅ Vehicle registered successfully"}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"message": f"❌ Registration failed: {str(e)}"}), 400
        finally:
            cursor.close()
            conn.close()
    return jsonify({"message": "❌ Database connection failed"}), 500

@app.route("/report_violation", methods=["POST"])
def report_violation():
    data = request.get_json()
    vehicle_number = data.get("vehicle_number")
    violation_type = data.get("violation_type")
    if not vehicle_number or not violation_type:
        return jsonify({"message": "❌ Missing vehicle number or violation type"}), 400
    weights = violation_weights.get(violation_type)
    if not weights:
        return jsonify({"message": "❌ Invalid violation type"}), 400
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE violations
                SET speeding_fines = speeding_fines + %s,
                    signal_violations = signal_violations + %s,
                    helmet_violations = helmet_violations + %s,
                    accidents = accidents + %s
                WHERE vehicle_number = %s
            """, (*weights, vehicle_number))
            conn.commit()
            return jsonify({"message": "✅ Violation reported successfully"}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({"message": f"❌ Failed to report violation: {str(e)}"}), 400
        