import socket
import threading
from distributed_version.shared.socket_utils import send_message, recv_message
from distributed_version.location_validator.location_validator import LocationValidator

HOST = "0.0.0.0"
PORT = 5002
NEXT_HOST = "localhost"
NEXT_PORT = 5003

def handle_client(conn: socket.socket, addr):
    try:
        with conn:
            message = recv_message(conn)
            errors = message.setdefault("errors", [])
            LocationValidator.validate(message, errors)
            with socket.create_connection((NEXT_HOST, NEXT_PORT)) as out:
                send_message(out, message)
            print(f"[location_validator] Processed order {message.get('order_id')}")
    except Exception as e:
        print(f"[location_validator] Error handling {addr}: {e}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[location_validator] Listening on port {PORT}...")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
