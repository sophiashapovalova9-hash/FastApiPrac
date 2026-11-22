import socket
import threading
from cryptography.fernet import Fernet

with open("secret.key", "rb") as f:
    cipher_suite = Fernet(f.read())

HOST, PORT = 'localhost', 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Сервер запущен на {HOST}:{PORT}...")

clients = {}
clients_lock = threading.Lock()
next_id = 1


def broadcast(sender_id, message):
    payload = cipher_suite.encrypt(f"[Клиент {sender_id}]: {message}".encode('utf-8'))
    with clients_lock:
        for cid, sock in list(clients.items()):
            if cid != sender_id:
                try:
                    sock.send(payload)
                except Exception:
                    pass


def handle_client(client_socket, client_id):
    print(f"Клиент {client_id} подключился.")
    try:
        while True:
            encrypted = client_socket.recv(4096)
            if not encrypted:
                break
            try:
                message = cipher_suite.decrypt(encrypted).decode('utf-8')
            except Exception:
                print(f"Клиент {client_id}: не удалось расшифровать.")
                continue
            print(f"Клиент {client_id}: {message}")
            broadcast(client_id, message)
    except ConnectionResetError:
        print(f"Клиент {client_id} разорвал соединение.")
    except Exception as e:
        print(f"Ошибка клиента {client_id}: {e}")
    finally:
        with clients_lock:
            clients.pop(client_id, None)
        client_socket.close()
        print(f"Клиент {client_id} отключён.")


while True:
    client_socket, addr = server_socket.accept()
    with clients_lock:
        cid = next_id
        next_id += 1
        clients[cid] = client_socket
    print(f"Подключился клиент {cid}: {addr}")
    threading.Thread(target=handle_client, args=(client_socket, cid), daemon=True).start()
