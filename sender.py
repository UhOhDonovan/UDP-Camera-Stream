import socket
import numpy as np
import cv2
import time
import random
import threading

# Specify IP information
LISTENER_IP = "127.0.0.1"
LISTENER_PORT = 12000
CHUNK_SIZE = 46080  # 576
NUM_CHUNKS = 20  # 1600

def listen(connection: socket.socket, addr: tuple[str, int]):
    try:
        msg = connection.recv(1024)
        RECEIVER_IP, RECIEVER_PORT = msg.decode().split(",")
        response = f"OK"
        connection.send(response.encode())
        connection.close()
        send_to_receiver(RECEIVER_IP, int(RECIEVER_PORT))
    except Exception as e:
        print(e)
    finally:
        connection.close()




def send_to_receiver(RECEIVER_IP: str, RECEIVER_PORT: int):

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
                sock.sendto(sequence_number + chunk.tobytes(), (RECEIVER_IP, RECEIVER_PORT))

            time.sleep(0.05)

    except KeyboardInterrupt:
        cap.release()
        cv2.destroyAllWindows()
    
    finally:
        sock.close()

def main():
    listener_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    listener_socket.bind((LISTENER_IP, LISTENER_PORT))
    listener_socket.listen(2)

    threads = []
    try: 
        while True:
            connection, addr = listener_socket.accept()
            
            new_thread = threading.Thread(target=listen, args=(connection, addr))
            new_thread.start()

            threads.append(new_thread)
    except Exception as e:
        print(e)
    finally:
        listener_socket.close()

if __name__ == "__main__":
    main()