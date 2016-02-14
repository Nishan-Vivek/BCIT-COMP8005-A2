from socket import *
import sys
from _thread import *

DEBUG = False;


def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)


def client_handler(client_socket, client_address):
    try:
        while True:
            data = client_socket.recv(1024)
            print_d('received "%s"' % data, DEBUG)
            if data:
                client_socket.sendall(data)
            else:
                break
    finally:
        client_socket.close()


if __name__ == '__main__':
    server_address = ('', 10000)
    listen_socket = socket(AF_INET, SOCK_STREAM)
    listen_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    listen_socket.bind(server_address)
    listen_socket.listen(5)
    while 1:
        print_d('waiting for connection...', True)
        client_socket, client_address = listen_socket.accept()
        print_d('...connected from:' + str(client_address), True)
        start_new_thread(client_handler, (client_socket,))




