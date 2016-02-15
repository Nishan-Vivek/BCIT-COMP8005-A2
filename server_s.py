import select
from socket import *
import sys
import queue
import signal
import csv

DEBUG = True
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
            write_stats(client_id_counter, client_data_counter)



            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)

class ClientStats():
    def __init__(self):
        self.client_id = 0
        self.data_sent = 0
        self.req_c = 0

def write_stats(client_id_counter, client_data_counter):
    server_statistics = {}

    for i, client_id in enumerate(client_id_counter):
        if client_id not in server_statistics:
            server_statistics[client_id] = ClientStats()
            server_statistics[client_id].client_id = client_id
            server_statistics[client_id].req_c += 1
            server_statistics[client_id].data_sent += client_data_counter[i]
        else:
            server_statistics[client_id].req_c += 1
            server_statistics[client_id].data_sent += client_data_counter[i]

    print_d("Writing stats to server_s_Stats.csv")
    with open('server_s_Stats.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, dialect='excel')
        filewriter.writerow(["ClientID", "Completed Connections", "Data Received"])
        for x in server_statistics:
            filewriter.writerow([server_statistics[x].client_id, server_statistics[x].req_c, server_statistics[x].data_sent])


def run_program():
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
                        client_id = ("{0}".format(client_addresses[sock]))
                        client_id_counter.append(client_id)
                        client_data_counter.append(sys.getsizeof(data_string))
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

client_id_counter = []
client_data_counter = []

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    run_program()
















