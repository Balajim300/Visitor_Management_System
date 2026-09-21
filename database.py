import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",
        database="visitor_management"
    )
    return connection

if __name__ == "__main__":
    db = get_db_connection()

    if db.is_connected():
        print("MySQL Connected Successfully!")

    db.close()