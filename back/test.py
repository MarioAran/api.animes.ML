import mysql.connector

def login():
    try:
        cnx = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user=input("user: "),
            password=input("passwd: "),
            database="sys"
        )
        print("✅ Conexión exitosa")
        cnx.close()
        return "Logged"
    except mysql.connector.Error as err:
        print(f"❌ Error conectando a MySQL: {err}")
        return "Error"

login()
