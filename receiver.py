import socket
import numpy as np
import cv2
import logging
import sys as sus
import datetime
import time

logging.basicConfig(
    filename=f"./tmp/{datetime.datetime.now()}-receiver.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(lineno)d %(message)s",
)
logger = logging.getLogger(__name__)

UDP_IP = "127.0.0.1"
UDP_PORT = 9999
CHUNK_SIZE = 46080 # 576  # size of each chunk
NUM_CHUNKS = 20 # 1600


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

dummy_chunk = np.zeros(CHUNK_SIZE, dtype=np.uint8)
data_sequence = np.zeros(CHUNK_SIZE * NUM_CHUNKS, dtype=np.uint8)

while True:
    try:
        data, addr = sock.recvfrom(CHUNK_SIZE + 3)
        sequence_number = int.from_bytes(data[0:3], "big")
        frame_data = data[3:]
        data_sequence[
            sequence_number * CHUNK_SIZE : (sequence_number + 1) * CHUNK_SIZE
        ] = (np.frombuffer(frame_data, dtype=np.uint8))
        frame = data_sequence.reshape(480, 640, 3)
        cv2.imshow("receiver", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    except Exception as e:
        ex_type, ex, tb = sus.exc_info()
        logger.error(f"{e} {tb.tb_lineno}")
        sus.exit()
