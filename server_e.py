import select
from socket import *
import sys
import queue

DEBUG = False
LISTEN_PORT = 10000
BUFFER_SIZE = 1024


def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)



# Setup Listening Socket
server_address = ('', LISTEN_PORT)
listen_socket = socket(AF_INET, SOCK_STREAM)
listen_socket.setblocking(0)
listen_socket.bind(server_address)
listen_socket.listen(5)

# Sockets to check with select
inputs = [listen_socket]

# Sockets ready to write to
outputs = []

# List of client addresses
client_addresses = {}

# Message queues (socket:Queue)
message_queues = {}

# Main loop through sockets with select
while inputs:
    print_d ("Waiting for available socket", DEBUG)
    readable, writeable, exceptional = select.select(inputs, outputs, inputs)

    #Loop through ready to read sockets
    for sock in readable:
        # Main listening socket
        if sock is listen_socket:
            client_socket, client_address = sock.accept()
            print_d("{0} connected.".format(client_address))
            client_socket.setblocking(0)
            inputs.append(client_socket) #Add client socket to list
            client_addresses[client_socket] = client_address
            message_queues[client_socket] = queue.Queue()
        # Client sockets
        else:
            try:
                data = sock.recv(BUFFER_SIZE)
                data_string = data.decode()
                if data:
                    print_d("Received: {0} ".format(data_string) + " from {0} ".format(client_addresses[sock]), DEBUG)
                    message_queues[sock].put(data)
                    if sock not in outputs:
                        outputs.append(sock)
                else: #connection closed
                    print_d("Closing connection with {0}, no data".format(client_addresses[sock]))
                    if sock in outputs:
                        outputs.remove(sock)
                    inputs.remove(sock)
                    sock.close()
                    del message_queues[sock]
            except Exception:
                print_d("Closing connection to {0}, exception on recv".format(client_addresses[sock]))
                if sock in outputs:
                    outputs.remove(sock)
                inputs.remove(sock)
                sock.close()
                del message_queues[sock]


    #Loop through ready to write sockets
    for sock in writeable:
        try:
            next_msg = message_queues[sock].get_nowait()
        except Exception:
            if sock in outputs:
                outputs.remove(sock)
        else:
            print_d("Sending " + next_msg.decode() + " to {0}".format(client_addresses[sock]), DEBUG)
            sock.sendall(next_msg)

    #Handle errored sockets
    for sock in exceptional:
        print_d("Closing connection to {0} due to socket exception".format(client_addresses[sock]))
        inputs.remove(sock)
        if sock in outputs:
            outputs.remove(sock)
        sock.close()
        del message_queues[sock]
















