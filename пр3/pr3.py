from multiprocessing import Process, Queue, Event, Lock
import time
import random

tasks = [
    "Задача 1 обработка транзакции",
    "Задача 2 валидация данных",
    "Задача 3 формирование отчёта",
    "Задача 4 архивация логов",
    "Задача 5 резервное копирование",
]


def data_processing(data_queue, log_queue, stop_event, lock):
    while not stop_event.is_set():
        task = random.choice(tasks)
        data_queue.put(task)
        log_queue.put(f"Обработка данных: {task}")
        with lock:
            print(f"Процесс обработки данных: {task}")
        time.sleep(random.uniform(0.5, 1.5))


def storage(data_queue, storage_queue, log_queue, stop_event, lock):
    while not stop_event.is_set():
        if not data_queue.empty():
            task = data_queue.get()
            storage_queue.put(task)
            log_queue.put(f"Сохранено в хранилище: {task}")
            with lock:
                print(f"Процесс хранения: сохранено {task}")
            time.sleep(random.uniform(0.5, 1.5))
        else:
            time.sleep(0.5)


def logging_process(log_queue, stop_event, lock):
    while not stop_event.is_set():
        if not log_queue.empty():
            record = log_queue.get()
            with lock:
                print(f"Процесс логирования: {record}")
        time.sleep(0.5)


if __name__ == "__main__":
    data_queue = Queue()
    storage_queue = Queue()
    log_queue = Queue()
    stop_event = Event()
    lock = Lock()

    processing_process = Process(
        target=data_processing,
        args=(data_queue, log_queue, stop_event, lock)
    )
    storage_process = Process(
        target=storage,
        args=(data_queue, storage_queue, log_queue, stop_event, lock)
    )
    logging_process_obj = Process(
        target=logging_process,
        args=(log_queue, stop_event, lock)
    )

    processing_process.start()
    storage_process.start()
    logging_process_obj.start()

    time.sleep(10)
    stop_event.set()

    processing_process.join()
    storage_process.join()
    logging_process_obj.join()

    print("Работа завершена")