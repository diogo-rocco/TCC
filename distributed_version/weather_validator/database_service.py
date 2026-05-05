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
                print("[weather_validator] Connected to MySQL.")
        except Error as e:
            print(f"[weather_validator] MySQL connection error: {e}")
            self.connection = None

    def open(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def get_city_inpe_code(self, city_name: str, uf: str):
        query = "SELECT inpe_code FROM city_inpe_code WHERE city = %s AND uf = %s"
        try:
            self.open()
            cursor = self.connection.cursor()
            cursor.execute(query, (city_name, uf))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Error as e:
            print(f"[weather_validator] Error fetching INPE code: {e}")
            return None

    def insert_city_inpe_code(self, city_name: str, uf: str, inpe_code: str):
        query = "INSERT INTO city_inpe_code (city, uf, inpe_code) VALUES (%s, %s, %s)"
        try:
            self.open()
            cursor = self.connection.cursor()
            cursor.execute(query, (city_name, uf, inpe_code))
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"[weather_validator] Error inserting INPE code: {e}")

    def get_weather_tag(self, weather_code: str):
        query = "SELECT weather_code_description FROM weather_code WHERE weather_code = %s"
        try:
            self.open()
            cursor = self.connection.cursor()
            cursor.execute(query, (weather_code,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Error as e:
            print(f"[weather_validator] Error fetching weather tag: {e}")
            return None
