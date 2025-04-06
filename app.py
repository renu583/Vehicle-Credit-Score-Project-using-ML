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
from route.gamification import gamification_bp

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
