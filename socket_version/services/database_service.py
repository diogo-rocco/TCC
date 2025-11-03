import pandas as pd
import mysql.connector
from mysql.connector import Error

class MySQLDatabase:
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
				database=self.database
			)
			if self.connection.is_connected():
				print("Connection to MySQL database was successful.")
		except Error as e:
			print(f"Error while connecting to MySQL: {e}")
			self.connection = None

	def close(self):
		if self.connection and self.connection.is_connected():
			self.connection.close()
			print("MySQL connection is closed.")
	
	def open(self):
		if not self.connection or not self.connection.is_connected():
			self.connect()

	def insert_order(self, order_data: dict):
		query = '''
			INSERT INTO orders (
				cep, requested_date, delivery_date, logradouro, bairro, localidade, uf, ibge_code, ddd, weather_tag, order_status
			) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		'''
		values = (order_data["cep"], 
			order_data["requested_date"], 
			order_data["delivery_date"], 
			order_data["logradouro"], 
			order_data["bairro"], 
			order_data["localidade"], 
			order_data["uf"], 
			order_data["ibge_code"], 
			order_data["ddd"], 
			order_data["weather_tag"], 
			order_data["order_status"])
		try:
			self.open()
			cursor = self.connection.cursor()
			cursor.execute(query, values)
			self.connection.commit()
			order_id = cursor.lastrowid
			cursor.close()
			return order_id
		except Error as e:
			print(f"Error inserting order: {e}")
			return None

	def insert_error_log(self, order_id: int, error_details: str):
		query = '''
			INSERT INTO errors (order_id, error_details)
			VALUES (%s, %s)
		'''
		values = (order_id, error_details)
		try:
			self.open()
			cursor = self.connection.cursor()
			cursor.execute(query, values)
			self.connection.commit()
			cursor.close()
		except Error as e:
			print(f"Error inserting error log: {e}")

