import socket
import sys
from _thread import *

DEBUG = False;


def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)


def client_thread(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print_d('connecting to %s port %s' % address)
    sock.connect(address)
    try:
        message = 'This is the message.  It will be repeated.'
        while True:
            print_d('sending "%s"' % message, DEBUG)
            sock.sendall(message.encode('utf-8'))
            amount_received = 0
            amount_expected = len(message)
            while amount_received < amount_expected:
                data = sock.recv(1024)
                amount_received += len(data)
                print_d('received "%s"' % data, DEBUG);
    finally:
        sock.close()


if __name__ == '__main__':
    server_address = ('localhost', 10000)
    # server_address = (sys.argv[1], 10000)
    print_d('i iz rnning')
    for x in range(1, 5):
        start_new_thread(client_thread, (server_address,))
