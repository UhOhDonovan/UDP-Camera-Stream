import socket
import numpy as np
import cv2
import logging
import sys as sus
import datetime

logging.basicConfig(
    filename=f"./tmp/{datetime.datetime.now()}-receiver.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(lineno)d %(message)s",
)
logger = logging.getLogger(__name__)

SENDER_IP = "127.0.0.1"
SENDER_PORT = 12000

def parse_args():
    if len(sus.argv) != 5:
        RECEIVER_IP = "127.0.0.1"
        RECEIVER_PORT = 9999
        CHUNK_SIZE = 46080 # 576  # size of each chunk
        NUM_CHUNKS = 20 # 1600
    else:
        RECEIVER_IP = sus.argv[1]
        RECEIVER_PORT = int(sus.argv[2])
        CHUNK_SIZE = int(sus.argv[3])  # 576  # size of each chunk
        NUM_CHUNKS = int(sus.argv[4])  # 1600
        assert(CHUNK_SIZE * NUM_CHUNKS == 921600)
    return RECEIVER_IP, RECEIVER_PORT, CHUNK_SIZE, NUM_CHUNKS

def receive(RECEIVER_IP, RECEIVER_PORT, CHUNK_SIZE, NUM_CHUNKS):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((RECEIVER_IP, RECEIVER_PORT))

    # dummy_chunk = np.zeros(CHUNK_SIZE, dtype=np.uint8)
    data_sequence = np.zeros(CHUNK_SIZE * NUM_CHUNKS, dtype=np.uint8)
    try:
        while True:
            data, addr = sock.recvfrom(CHUNK_SIZE + 3)
            sequence_number = int.from_bytes(data[0:3], "big")
            frame_data = data[3:]
            data_sequence[
                sequence_number * CHUNK_SIZE : (sequence_number + 1) * CHUNK_SIZE
            ] = np.frombuffer(frame_data, dtype=np.uint8)
            frame = data_sequence.reshape(480, 640, 3)
            cv2.imshow("receiver", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except Exception as e:
        ex_type, ex, tb = sus.exc_info()
        logger.error(f"{e} {tb.tb_lineno}")
    finally:
        sock.close()
    

def initiate_connection(RECEIVER_IP, RECEIVER_PORT, CHUNK_SIZE, NUM_CHUNKS):
    try:
        client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        client_socket.connect((SENDER_IP, SENDER_PORT))
        request = f"{RECEIVER_IP},{RECEIVER_PORT}"
        client_socket.send(request.encode())

        data = b""
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break

            data += chunk

        assert data.decode() == "OK"
        receive(RECEIVER_IP, RECEIVER_PORT, CHUNK_SIZE, NUM_CHUNKS)
    finally:
        client_socket.close()


def main():
    RECEIVER_IP, RECEIVER_PORT, CHUNK_SIZE, NUM_CHUNKS = parse_args()
    initiate_connection(RECEIVER_IP, RECEIVER_PORT, CHUNK_SIZE, NUM_CHUNKS)


if __name__ == "__main__":
    main()
