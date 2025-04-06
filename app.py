
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import joblib
import numpy as np
from db import get_db_connection
from gamification import gamification_bp

app = Flask(__name__)
CORS(app)  # Enable CORS
app.register_blueprint(gamification_bp, url_prefix="/gamification")

# Paths for model and scaler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "credit_score_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

# Load model and scaler
model = scaler = None
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ Model & Scaler Loaded Successfully")
except Exception as e:
    print("❌ Model loading failed:", e)

# Violation type weights
violation_weights = {
    "overspeeding": [1, 0, 0, 0],
    "signal_jumping": [0, 1, 0, 0],
    "no_helmet_seatbelt": [0, 0, 1, 0],
    "drunk_driving": [1, 1, 1, 1],
    "triple_riding": [0, 0, 1, 0],
    "no_violation_month": [-0.5, -0.5, -0.5, -0.5],
    "fine_paid_on_time": [-0.2, -0.2, -0.2, -0.2]
}

# Homepage route
@app.route("/")
def home():
    return render_template("index.html")

# Register a vehicle
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
            cursor.execute(
                "INSERT INTO vehicles (vehicle_number, owner_name) VALUES (%s, %s)",
                (vehicle_number, owner_name)
            )
            cursor.execute(
                "INSERT INTO violations (vehicle_number) VALUES (%s)",
                (vehicle_number,)
            )
            conn.commit()
            return jsonify({"message": "✅ Vehicle registered successfully"}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"message": f"❌ Registration failed: {str(e)}"}), 400
        finally:
            cursor.close()
            conn.close()
    return jsonify({"message": "❌ Database connection failed"}), 500

# Report a violation
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
        finally:
            cursor.close()
            conn.close()
    return jsonify({"message": "❌ Database connection failed"}), 500

# Predict credit score by vehicle number
@app.route("/predict_score/<vehicle_number>", methods=["GET"])
def predict_score(vehicle_number):
    if not model or not scaler:
        return jsonify({"error": "❌ Model or scaler not loaded"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT speeding_fines, signal_violations, helmet_violations, accidents
                FROM violations
                WHERE vehicle_number = %s
            """, (vehicle_number,))
            record = cursor.fetchone()

            if not record:
                return jsonify({"error": "❌ Vehicle not found"}), 404

            input_data = np.array([[record['speeding_fines'], record['signal_violations'],
                                    record['helmet_violations'], record['accidents']]])
            scaled_data = scaler.transform(input_data)
            predicted_score = model.predict(scaled_data)[0]

            return jsonify({"credit_score": round(predicted_score, 2)}), 200
        except Exception as e:
            return jsonify({"error": f"❌ Prediction failed: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({"error": "❌ Database connection failed"}), 500

# Run the Flask server
if __name__ == "__main__":
    app.run(debug=True, port=5001)

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import os
from flask import Flask, request,render_template, jsonify
import joblib
import numpy as np
from gamification import gamification_bp

 # Your gamification blueprint
import os

# Initialize Flask app
app = Flask(__name__)
app.register_blueprint(gamification_bp, url_prefix="/gamification")


@app.route('/')
def home():
    return render_template("index.html")

# Load model and scaler
MODEL_PATH = os.path.join("model","credit_score_model.pkl")
SCALER_PATH = os.path.join("model","scaler.pkl")



try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    print("❌ Failed to load model or scaler:", str(e))
    model, scaler = None, None


@app.route("/predict", methods=["POST"])
def predict():
    if model is None or scaler is None:
        return jsonify({"error": "Model or scaler not loaded"}), 500

    try:
        data = request.get_json()
        required_fields = ["speeding_fines", "signal_violations", "helmet_violations", "accidents"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing input fields"}), 400

        # Prepare and scale input
        input_data = np.array([[data["speeding_fines"], data["signal_violations"],
                                data["helmet_violations"], data["accidents"]]])
        input_scaled = scaler.transform(input_data)
        predicted_score = model.predict(input_scaled)[0]

        return jsonify({"predicted_credit_score": round(predicted_score, 2)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
    

