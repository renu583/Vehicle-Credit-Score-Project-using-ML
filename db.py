import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="vehicle_credit_db"
        )
        print("✅ MySQL Connected successfully!")
        return conn
    except mysql.connector.Error as err:
        print("❌ Error connecting to DB:", err)
        return None
