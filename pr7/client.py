import socket
import threading
from cryptography.fernet import Fernet

with open("secret.key", "rb") as f:
    cipher_suite = Fernet(f.read())

HOST = input("Адрес (по умолчанию localhost): ") or "localhost"
PORT = int(input("Порт (по умолчанию 12345): ") or 12345)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((HOST, PORT))
    print(f"Подключено к {HOST}:{PORT}")
except Exception as e:
    print(f"Ошибка подключения: {e}")
    exit(1)


def receive_messages():
    while True:
        try:
            encrypted = client_socket.recv(4096)
            if not encrypted:
                print("Сервер закрыл соединение.")
                break
            print(f"\n{cipher_suite.decrypt(encrypted).decode('utf-8')}\n> ", end="")
        except Exception as e:
            print(f"\nОшибка приёма: {e}")
            break
    client_socket.close()


threading.Thread(target=receive_messages, daemon=True).start()

try:
    while True:
        msg = input("> ")
        if msg.strip().lower() in ("exit", "quit"):
            break
        client_socket.send(cipher_suite.encrypt(msg.encode('utf-8')))
except KeyboardInterrupt:
    print("\nВыход...")
finally:
    client_socket.close()