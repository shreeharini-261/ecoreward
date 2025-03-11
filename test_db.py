import mysql.connector
from mysql.connector import Error

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'damn',
    'database': 'ecorewards'
}

try:
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("✅ Database connected successfully!")
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("Available tables:", tables)
except Error as e:
    print(f"❌ Database connection failed: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
