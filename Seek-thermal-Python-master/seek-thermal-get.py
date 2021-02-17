import socket
from time import time
import cv2
import pickle
import struct

HOST='192.168.2.53'
PORT=9001

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(10)
conn,addr=s.accept()

data = b''
payload_size = struct.calcsize("L")
t0 = time()
while True:
    t = time()
    print("fps:", 1 / (t - t0))
    t0 = time()
    while len(data) < payload_size:
        data += conn.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0]
    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame=pickle.loads(frame_data)
    print(frame)


    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', 1280, 720)
    cv2.imshow('frame',frame)

    cv2.waitKey(1)
