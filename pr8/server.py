import socket
import cv2
import numpy as np
import time

HOST = 'localhost'
PORT = 12345
JPEG_QUALITY = 70
FPS_LIMIT = 30
VIDEO_FILE = 'video.mp4'   # положите файл рядом со скриптом


def create_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    return server_socket


def open_capture():
    cap = cv2.VideoCapture(VIDEO_FILE)
    if not cap.isOpened():
        raise RuntimeError(f"Не удалось открыть видеофайл: {VIDEO_FILE}")
    return cap


def main():
    server_socket = create_server()
    print(f"Сервер запущен на {HOST}:{PORT}. Ожидание клиента...")

    cap = open_capture()
    frame_time = 1.0 / FPS_LIMIT

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Клиент подключен: {addr}")
            client_socket.settimeout(5.0)

            try:
                while True:
                    start = time.time()
                    ret, frame = cap.read()
                    if not ret:
                        # зацикливаем видео
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue

                    _, encoded = cv2.imencode(
                        '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
                    )
                    data = encoded.tobytes()

                    try:
                        client_socket.sendall(len(data).to_bytes(4, 'big') + data)
                    except (BrokenPipeError, ConnectionResetError, socket.timeout):
                        print("Клиент отключился. Ожидание нового подключения...")
                        break

                    cv2.imshow('Server - Video File', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        raise SystemExit

                    elapsed = time.time() - start
                    if elapsed < frame_time:
                        time.sleep(frame_time - elapsed)

            finally:
                client_socket.close()
                print("Соединение с клиентом закрыто.")

    except KeyboardInterrupt:
        print("\nОстановка сервера (Ctrl+C).")
    except SystemExit:
        print("Выход по клавише q.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        server_socket.close()


if __name__ == '__main__':
    main()