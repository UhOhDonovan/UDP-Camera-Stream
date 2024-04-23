import socket
import numpy as np
import time
import cv2
import heapq

UDP_IP="127.0.0.1"
UDP_PORT = 9999
CHUNK_SIZE = 46080  # size of each chunk
NUM_CHUNKS = 20


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

data_sequence = []

while True:
    data, addr = sock.recvfrom(46082)
    sequence_number = int.from_bytes(data[0:2], "big")
    frame_data = data[2:]
    heapq.heappush(data_sequence, (sequence_number, frame_data))
    if len(data_sequence) == NUM_CHUNKS:
        # sorted_chunks = sorted(data_sequence, key=lambda x: x[0])
        frame = np.concatenate([np.frombuffer(chunk[1], dtype=np.uint8) for chunk in data_sequence])
        frame = frame.reshape(480,640,3)
        cv2.imshow('receiver', frame)

        data_sequence = []
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
