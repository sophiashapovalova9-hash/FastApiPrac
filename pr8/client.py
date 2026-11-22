import socket
import numpy as np
import cv2
import time

HOST = 'localhost'
PORT = 12345
RECONNECT_DELAY = 2


def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        packet = sock.recv(n - len(buf))
        if not packet:
            return None
        buf += packet
    return buf


def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10.0)
    client_socket.connect((HOST, PORT))
    print("Подключено к серверу")

    try:
        while True:
            size_bytes = recv_exact(client_socket, 4)
            if size_bytes is None:
                raise ConnectionError("Сервер закрыл соединение")
            img_size = int.from_bytes(size_bytes, 'big')

            data = recv_exact(client_socket, img_size)
            if data is None:
                raise ConnectionError("Сервер закрыл соединение")

            img_array = np.frombuffer(data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is not None:
                cv2.imshow('Client - Video Stream', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                raise SystemExit

    finally:
        client_socket.close()


def main():
    try:
        while True:
            try:
                run_client()
            except SystemExit:
                print("Выход по клавише q.")
                break
            except (ConnectionError, ConnectionResetError, BrokenPipeError,
                    socket.timeout, OSError) as e:
                print(f"Соединение потеряно: {e}. Переподключение через {RECONNECT_DELAY} сек...")
                time.sleep(RECONNECT_DELAY)
    except KeyboardInterrupt:
        print("\nОстановка клиента (Ctrl+C).")
    finally:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()