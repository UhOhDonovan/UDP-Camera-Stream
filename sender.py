import socket
import cv2
import time
import threading
import logging
import datetime
logging.basicConfig(
    filename=f"./tmp/{datetime.datetime.now()}-sender.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(lineno)d %(message)s",
)
logger = logging.getLogger(__name__)

# Specify IP information (Not sure if should be hardcoded or parsed)
LISTENER_IP = "127.0.0.1"
LISTENER_PORT = 12000
CHUNK_SIZE = 46080  # 576
NUM_CHUNKS = 20  # 1600


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
    cap = cv2.VideoCapture(
        0
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
