import cv2
import numpy as np

VIDEO_FILE = 'video.mp4'


def measure_frame_size(quality, frames=30):
    cap = cv2.VideoCapture(VIDEO_FILE)
    if not cap.isOpened():
        print(f"Не удалось открыть {VIDEO_FILE}")
        return None
    sizes = []
    for _ in range(frames):
        ret, frame = cap.read()
        if not ret:
            break
        _, enc = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        sizes.append(len(enc.tobytes()))
    cap.release()
    return sum(sizes) / len(sizes) if sizes else None


if __name__ == '__main__':
    print(f"{'Качество JPEG':<15}{'Ср. размер кадра (байт)':<25}")
    print("-" * 40)
    for q in [30, 50, 70, 90, 95]:
        avg = measure_frame_size(q)
        if avg:
            print(f"{q:<15}{avg:<25.0f}")