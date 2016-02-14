import socket
import sys
from multiprocessing import Pool
import time
from math import floor, sqrt

SERVER_PORT = 10000
SERVER_ADDRESS = 'localhost'
nb_repeat = 200

def client_connection(*args):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (sys.argv[1], 10000)
    print ('connecting to %s port %s' % server_address)
    sock.connect(server_address)

    try:
        message = "This is the message.  It will be repeated."
        while True:
            print('sending "%s"' % message)
            sock.sendall(message.encode())
            amount_received = 0
            amount_expected = len(message)
            # while amount_received < amount_expected:
            data = sock.recv(1024).decode()
            # amount_received += len(data)
            print('received "%s"' % data);

    finally:
        sock.close()



if __name__ == '__main__':
    pool = Pool(processes=nb_repeat)
    results = pool.map(client_connection, [None for _ in range(nb_repeat)])