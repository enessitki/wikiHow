import socket
import time


UDP_IP = "192.168.1.250"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM | socket.SOCK_CLOEXEC | socket.SOCK_NONBLOCK | socket.IPPROTO_IP)  # UDP

sock.settimeout(0)

while True:
    t0 = time.time()
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    print(time.time() - t0)
    time.sleep(1)


