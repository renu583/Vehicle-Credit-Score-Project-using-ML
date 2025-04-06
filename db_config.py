import mysql.connector
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Update if needed
            user="root",
            password="root123",
            database="vehicle_credit_db"
        )
        print("Connected successfully!")
        return conn
    except mysql.connector.Error as err:
        print("Error:", err)
        return None

def fetch_vehicle_fines():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM vehicle_fines;")
                results = cursor.fetchall()
                for row in results:
                    print(row)
        except mysql.connector.Error as err:
            print("Error executing query:", err)
        finally:
            conn.close()

# Execute the function
fetch_vehicle_fines()




