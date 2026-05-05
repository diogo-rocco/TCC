import os
import socket
import threading
from dotenv import load_dotenv
from distributed_version.shared.socket_utils import send_message, recv_message
from distributed_version.weather_validator.weather_validator import WeatherValidator
from distributed_version.weather_validator.database_service import DatabaseService

load_dotenv()

HOST = "0.0.0.0"
PORT = 5003
NEXT_HOST = "localhost"
NEXT_PORT = 5004

db_service: DatabaseService = None
db_lock = threading.Lock()

def handle_client(conn: socket.socket, addr):
    try:
        with conn:
            message = recv_message(conn)
            errors = message.setdefault("errors", [])
            warnings = message.setdefault("warnings", [])
            with db_lock:
                WeatherValidator.validate(message, errors, warnings, db_service)
            with socket.create_connection((NEXT_HOST, NEXT_PORT)) as out:
                send_message(out, message)
            print(f"[weather_validator] Processed order {message.get('order_id')}")
    except Exception as e:
        print(f"[weather_validator] Error handling {addr}: {e}")

def main():
    global db_service
    db_service = DatabaseService(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[weather_validator] Listening on port {PORT}...")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
