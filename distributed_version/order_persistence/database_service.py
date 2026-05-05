import mysql.connector
from mysql.connector import Error

class DatabaseService:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            if self.connection.is_connected():
                print("[order_persistence] Connected to MySQL.")
        except Error as e:
            print(f"[order_persistence] MySQL connection error: {e}")
            self.connection = None

    def open(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def insert_order(self, order_data: dict):
        query = """
            INSERT INTO orders (
                cep, requested_date, delivery_date, logradouro, bairro,
                localidade, uf, ibge_code, ddd, weather_tag, order_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            order_data.get("cep"),
            order_data.get("requested_date"),
            order_data.get("delivery_date"),
            order_data.get("logradouro"),
            order_data.get("bairro"),
            order_data.get("localidade"),
            order_data.get("uf"),
            order_data.get("ibge_code"),
            order_data.get("ddd"),
            order_data.get("weather_tag"),
            order_data.get("order_status"),
        )
        try:
            self.open()
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
            order_id = cursor.lastrowid
            cursor.close()
            return order_id
        except Error as e:
            print(f"[order_persistence] Error inserting order: {e}")
            return None

    def insert_error_log(self, order_id: int, error_details: str):
        query = "INSERT INTO errors (order_id, error_details) VALUES (%s, %s)"
        try:
            self.open()
            cursor = self.connection.cursor()
            cursor.execute(query, (order_id, error_details))
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"[order_persistence] Error inserting error log: {e}")
