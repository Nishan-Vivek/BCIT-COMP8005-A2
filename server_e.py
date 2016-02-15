import select
from socket import *
import sys
import queue
import signal
import time

DEBUG = False
LISTEN_PORT = 10000
BUFFER_SIZE = 1024

def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if input("\nReally quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)

def run_program():
    # Main Loop
    while True:
        events = epoll.poll(1)
        for fileno, event in events:

            # handle readable client connections
            if event & select.EPOLLIN:
                # handle new connection requests on listen socket
                if fileno == listen_socket.fileno():
                    client_socket, client_address = listen_socket.accept()
                    print_d("{0} connected.".format(client_address))
                    client_socket.setblocking(0)
                    epoll.register(client_socket.fileno(), select.EPOLLIN | select.EPOLLET)
                    client_addresses[client_socket.fileno()] = client_address
                    client_sockets[client_socket.fileno()] = client_socket
                    message_queues[client_socket.fileno()] = queue.Queue()
                    epoll.modify(listen_socket.fileno(), select.EPOLLIN | select.EPOLLET)
                else:
                    try:
                        data = client_sockets[fileno].recv(BUFFER_SIZE)
                        data_string = data.decode()
                        if data:
                            print_d("Received: {0} ".format(data_string) + " from {0} ".format(client_addresses[fileno]), DEBUG)
                            message_queues[fileno].put(data)
                            epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                        else: #close connection
                            print_d("Closing connection with {0}, no data".format(client_addresses[fileno]))
                            epoll.unregister(fileno)
                            client_sockets[fileno].close()
                            del message_queues[fileno]
                            del client_addresses[fileno]
                            del client_sockets[fileno]
                    except Exception as e:
                        print_d("Closing connection to {0}, ".format(client_addresses[fileno]) + repr(e))
                        epoll.unregister(fileno)
                        client_sockets[fileno].close()
                        del message_queues[fileno]
                        del client_addresses[fileno]
                        del client_sockets[fileno]

            # handle writeable connections
            elif event & select.EPOLLOUT:
                try:
                    next_msg = message_queues[fileno].get_nowait()
                except Exception:
                    print_d("Closing connection to {0}, ".format(client_addresses[fileno]) + repr(e))
                    epoll.unregister(fileno)
                    client_sockets[fileno].close()
                    del message_queues[fileno]
                    del client_addresses[fileno]
                    del client_sockets[fileno]
                else:
                    try:
                        print_d("Sending " + next_msg.decode() + " to {0}".format(client_addresses[fileno]), DEBUG)
                        client_sockets[fileno].sendall(next_msg)
                        epoll.modify(fileno, select.EPOLLIN | select.EPOLLET)
                    except Exception:
                        print_d("Closing connection to {0}, ".format(client_addresses[fileno]) + repr(e))
                        epoll.unregister(fileno)
                        client_sockets[fileno].close()
                        del message_queues[fileno]
                        del client_addresses[fileno]
                        del client_sockets[fileno]

            # handle closed or erroneous connections
            else:
                pass
                # print_d("Closing connection to {0}".format(client_addresses[fileno]))
                # epoll.unregister(fileno)
                # client_sockets[fileno].close()
                # del message_queues[fileno]
                # del client_addresses[fileno]
                # del client_sockets[fileno]  # # Sockets ready to write to

class ClientStats():
    def __init__(self):
        self.client_id = 0
        self.req_c = 0
        self.data_sent = 0


# Setup Listening Socket
server_address = ('', LISTEN_PORT)
listen_socket = socket(AF_INET, SOCK_STREAM)
listen_socket.setblocking(0)
listen_socket.bind(server_address)
listen_socket.listen(5)

#Dictionaries to track clients and messages.
message_queues = {}
client_addresses = {}
client_sockets = {}

# create epoll object and register listing socket
epoll = select.epoll()
epoll.register(listen_socket.fileno(), select.EPOLLIN | select.EPOLLET)

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    run_program()




