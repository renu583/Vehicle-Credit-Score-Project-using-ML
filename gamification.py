from flask import Blueprint, jsonify, request
from database import get_db_connection

gamification_bp = Blueprint("gamification", __name__)

POINTS = {
    "overspeeding": -10,
    "signal_jumping": -15,
    "drunk_driving": -20,
    "triple_riding": -8,
    "no_helmet_seatbelt": -5,
    "no_violation_month": +10,
    "fine_paid_on_time": +5
}

@gamification_bp.route("/report_violation", methods=["POST"])
def report_violation():
    data = request.json
    vehicle_number = data.get("vehicle_number")
    violation_type = data.get("violation_type")

    if not vehicle_number or violation_type not in POINTS:
        return jsonify({"error": "Invalid data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM user_scores WHERE vehicle_number = %s", (vehicle_number,))
    result = cursor.fetchone()

    if result:
        new_score = max(result[0] + POINTS.get(violation_type, 0), 0)
        cursor.execute("UPDATE user_scores SET score = %s WHERE vehicle_number = %s", (new_score, vehicle_number))
    else:
        new_score = max(100 + POINTS.get(violation_type, 0), 0)
        cursor.execute("INSERT INTO user_scores (vehicle_number, score) VALUES (%s, %s)", (vehicle_number, new_score))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Score updated", "new_score": new_score})
