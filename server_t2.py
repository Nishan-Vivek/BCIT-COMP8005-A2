from socket import *
import threading
import sys

DEBUG = False
LISTEN_PORT = 10000
BUFFER_SIZE = 1024


def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)


class Client_HandlerThread(threading.Thread):

    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        print_d("Thread created for {0}".format(client_address))

    def run(self):
        while 1:
            try:
                data = self.client_socket.recv(BUFFER_SIZE)
                data_string = data.decode()
                if data:
                    print_d("Received: {0} ".format(data_string) + " from {0} ".format(self.client_address), DEBUG)
                    self.client_socket.sendall(data)
                else: #connection closed
                    print_d("Closing connection with {0}, no data".format(self.client_address))
                    self.client_socket.close()
                    break
            except Exception:
                    print_d("Closing connection with {0}, due to exception".format(self.client_address))
                    self.client_socket.close()
                    break
        self.client_socket.close()
        print_d("Thread ending for {0}".format(self.client_address))


# Setup Listening Socket
server_address = ('', LISTEN_PORT)
listen_socket = socket(AF_INET, SOCK_STREAM)
# listen_socket.setblocking(0)
listen_socket.bind(server_address)

#Main loop
while 1:
    print_d ("Waiting for connection")
    listen_socket.listen(5)
    client_socket, client_address = listen_socket.accept()
    newClientThread = Client_HandlerThread(client_socket, client_address)
    newClientThread.start()

