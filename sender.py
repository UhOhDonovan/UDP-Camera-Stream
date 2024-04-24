import socket
import numpy as np
import cv2
import time


# Specify IP information
UDP_IP = '127.0.0.1'                  
UDP_PORT = 9999
CHUNK_SIZE = 46080

cap = cv2.VideoCapture(0) # Capture video element
while(True):
    ret, frame = cap.read()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    d = frame.flatten()
    s = d.tobytes()
    for i in range(20):
        sequence_number = i.to_bytes(2, "big")
        start_idx = i * CHUNK_SIZE
        end_idx = (i + 1) * CHUNK_SIZE
        chunk = s[start_idx:end_idx]
        sock.sendto(sequence_number + chunk, (UDP_IP, UDP_PORT))
    
    time.sleep(0.002)
    

cap.release()
cv2.destroyAllWindows()
