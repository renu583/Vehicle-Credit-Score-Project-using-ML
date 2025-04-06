from flask import Blueprint, jsonify
from database import get_db_connection

fines_bp = Blueprint("fines", __name__)

@fines_bp.route("/get_fines", methods=["GET"])
def get_fines():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicle_fines;")
    fines = cursor.fetchall()
    conn.close()
    return jsonify(fines)
