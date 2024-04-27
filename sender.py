import socket
import cv2
import time
import threading
import logging
import datetime
import sys as sus
logging.basicConfig(
    filename=f"./tmp/{datetime.datetime.now()}-sender.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(lineno)d %(message)s",
)
logger = logging.getLogger(__name__)

# Specify IP information (Not sure if should be hardcoded or parsed)

LISTENER_IP: str = sus.argv[1] if len(sus.argv) >= 2 else "127.0.0.1"
LISTENER_PORT: int = int(sus.argv[2]) if len(sus.argv) >= 3 else 12000
CHUNK_SIZE: int = 46080  # 576
NUM_CHUNKS: int = 20  # 1600
assert NUM_CHUNKS * CHUNK_SIZE == 921600 # Assert camera resolution is 480p

def find_available_devices():
    capture_indexes = []

    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if (width, height) == (640, 480):
                logger.info(f"Device found at index {i}")
                capture_indexes.append(i)
        cap.release()
    
    return capture_indexes

AVAILABLE_DEVICES: list[int] = find_available_devices()
logger.info(f"Available Devices: {AVAILABLE_DEVICES}")

def handle_connection(connection: socket.socket, addr: tuple[str, int]):
    try:
        msg = connection.recv(1024)
        RECEIVER_IP, RECIEVER_PORT = msg.decode().split(",")
        logger.info(f"Request received for {RECEIVER_IP}:{RECIEVER_PORT}")
        response = f"OK"
        connection.send(response.encode())
        send_to_receiver(RECEIVER_IP, int(RECIEVER_PORT))
    except Exception as e:
        logger.error(e)
    finally:
        connection.close()


def send_to_receiver(RECEIVER_IP: str, RECEIVER_PORT: int):
    logger.info(f"Opening UDP Socket to {RECEIVER_IP}:{RECEIVER_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    capture_index = AVAILABLE_DEVICES.pop()
    cap = cv2.VideoCapture(
        capture_index
    )  # Functionality for multiple devices needs to be implemented
    i = -1
    try:
        while True:
            i += 1
            i %= NUM_CHUNKS
            if not i:
                _, frame = cap.read()
            d = frame.flatten()
            sequence_number = i.to_bytes(3, "big")
            start_idx = i * CHUNK_SIZE
            end_idx = (i + 1) * CHUNK_SIZE
            chunk = d[start_idx:end_idx]
            sock.sendto(sequence_number + chunk.tobytes(), (RECEIVER_IP, RECEIVER_PORT))

            time.sleep(0.002)
    finally:
        logger.info(f"Media stream terminated, closing video capture")
        sock.close()
        cap.release()
        cv2.destroyAllWindows()
        AVAILABLE_DEVICES.insert(0, capture_index)


def main():
    logger.info(f"Listening at {LISTENER_IP}:{LISTENER_PORT}")
    listener_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    listener_socket.bind((LISTENER_IP, LISTENER_PORT))
    listener_socket.listen(2)

    threads = []
    try:
        while True:
            connection, addr = listener_socket.accept()
            logger.info(f"Connection received from {addr}")

            new_thread = threading.Thread(target=handle_connection, args=(connection, addr))
            new_thread.start()

            threads.append(new_thread)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected. Closing sockets...")
        # Close all threads and sockets
        for thread in threads:
            thread.join()  # Wait for threads to finish
    except Exception as e:
        logger.error(e)
    finally:
        listener_socket.close()


if __name__ == "__main__":
    main()
