import socket
import sys


def print_d(message,debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)

debug = True;


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port on the server given by the caller
server_address = (sys.argv[1], 10000)
print_d ('connecting to %s port %s' % server_address, debug)
sock.connect(server_address)

try:

    message = 'This is the message.  It will be repeated.'
    while True:
        print_d('sending "%s"' % message, debug)
        sock.sendall(message.encode('utf-8'))

        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(1024)
            amount_received += len(data)
            print_d('received "%s"' % data, debug);

finally:
    sock.close()
