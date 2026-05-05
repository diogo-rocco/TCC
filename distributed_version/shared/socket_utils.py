import json
import socket

def send_message(sock: socket.socket, data: dict) -> None:
    payload = json.dumps(data, default=str).encode("utf-8")
    sock.sendall(len(payload).to_bytes(4, "big") + payload)

def recv_message(sock: socket.socket) -> dict:
    raw_len = _recvall(sock, 4)
    if not raw_len:
        raise ConnectionError("Connection closed before message length received")
    msg_len = int.from_bytes(raw_len, "big")
    payload = _recvall(sock, msg_len)
    if not payload:
        raise ConnectionError("Connection closed before full message received")
    return json.loads(payload.decode("utf-8"))

def _recvall(sock: socket.socket, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
