import socket
import numpy as np
import cv2
import time
import random

# Specify IP information
UDP_IP = "127.0.0.1"
UDP_PORT = 9999
CHUNK_SIZE = 46080  # 576
NUM_CHUNKS = 20  # 1600

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0)  # Capture video element
try:
    while True:
        _, frame = cap.read()
        d = frame.flatten()
        numbers = list(range(NUM_CHUNKS))
        random.shuffle(numbers)
        for i in numbers:
            sequence_number = i.to_bytes(3, "big")
            start_idx = i * CHUNK_SIZE
            end_idx = (i + 1) * CHUNK_SIZE
            chunk = d[start_idx:end_idx]
            sock.sendto(sequence_number + chunk.tobytes(), (UDP_IP, UDP_PORT))

        time.sleep(0.05)        

except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
