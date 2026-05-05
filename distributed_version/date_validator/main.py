import socket
import threading
from distributed_version.shared.socket_utils import send_message, recv_message
from distributed_version.date_validator.date_validator import DateValidator

HOST = "0.0.0.0"
PORT = 5001
NEXT_HOST = "localhost"
NEXT_PORT = 5002

def handle_client(conn: socket.socket, addr):
    try:
        with conn:
            message = recv_message(conn)
            errors = message.setdefault("errors", [])
            warnings = message.setdefault("warnings", [])
            DateValidator.validate(message, errors, warnings)
            with socket.create_connection((NEXT_HOST, NEXT_PORT)) as out:
                send_message(out, message)
            print(f"[date_validator] Processed order {message.get('order_id')}")
    except Exception as e:
        print(f"[date_validator] Error handling {addr}: {e}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[date_validator] Listening on port {PORT}...")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
