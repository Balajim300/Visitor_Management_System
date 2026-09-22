import os
import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "localhost"),
        port=int(os.getenv("MYSQLPORT", "3306")),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", ""),
        database=os.getenv("MYSQLDATABASE", "visitor_management")
    )

    return connection


if __name__ == "__main__":
    db = get_db_connection()

    if db.is_connected():
        print("MySQL Connected Successfully!")

    db.close()
