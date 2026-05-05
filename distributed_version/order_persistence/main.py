import os
import socket
import threading
from dotenv import load_dotenv
from distributed_version.shared.socket_utils import recv_message
from distributed_version.order_persistence.database_service import DatabaseService

load_dotenv()

HOST = "0.0.0.0"
PORT = 5004

db_service: DatabaseService = None
db_lock = threading.Lock()

def handle_client(conn: socket.socket, addr):
    try:
        with conn:
            message = recv_message(conn)
            errors = message.get("errors", [])
            message["order_status"] = "OK" if not errors else "ERROR"
            message["errors"] = "; ".join(errors)

            with db_lock:
                order_id = db_service.insert_order(message)
                if errors and order_id:
                    db_service.insert_error_log(order_id, message["errors"])

            print(f"[order_persistence] Persisted order {message.get('order_id')} → status={message['order_status']}")
    except Exception as e:
        print(f"[order_persistence] Error handling {addr}: {e}")

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
        print(f"[order_persistence] Listening on port {PORT}...")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
