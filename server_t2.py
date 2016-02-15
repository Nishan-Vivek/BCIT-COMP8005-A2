from socket import *
import threading
import sys
import queue
import signal
import csv

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
            write_stats(q)

            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)

class Client_HandlerThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        print_d("Thread created for {0}".format(client_address))

    def run(self):
        client_id_counter = []
        client_data_counter = []
        while 1:
            try:
                data = self.client_socket.recv(BUFFER_SIZE)
                data_string = data.decode()
                if data:
                    print_d("Received: {0} ".format(data_string) + " from {0} ".format(self.client_address), DEBUG)
                    client_id = ("{0}".format(self.client_address))
                    client_id_counter.append(client_id)
                    client_data_counter.append(sys.getsizeof(data_string))
                    self.client_socket.sendall(data)
                else:  # connection closed
                    print_d("Closing connection with {0}, no data".format(self.client_address))
                    self.client_socket.close()
                    break
            except Exception:
                print_d("Closing connection with {0}, due to exception".format(self.client_address))
                self.client_socket.close()
                break
        self.client_socket.close()
        server_statistics = {}

        print_d("Thread ending for {0}".format(self.client_address))
        for i, client_id in enumerate(client_id_counter):
            if client_id not in server_statistics:
                server_statistics[client_id] = ClientStats()
                server_statistics[client_id].client_id = client_id
                server_statistics[client_id].req_c += 1
                server_statistics[client_id].data_sent += client_data_counter[i]
            else:
                server_statistics[client_id].req_c += 1
                server_statistics[client_id].data_sent += client_data_counter[i]

        q.put(server_statistics)



class ClientStats():
    def __init__(self):
        self.client_id = 0
        self.data_sent = 0
        self.req_c = 0


def write_stats(q):
    server_statistics = {}

    while not q.empty():
        server_statistics.update(q.get())

    print_d("Writing stats to server_t_Stats.csv")
    with open('server_t_Stats.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, dialect='excel')
        filewriter.writerow(["ClientID", "Completed Connections", "Data Received"])
        for x in server_statistics:
            filewriter.writerow(
                [server_statistics[x].client_id, server_statistics[x].req_c, server_statistics[x].data_sent])



def run_program():
# Main loop
    while 1:
        print_d("Waiting for connection")
        listen_socket.listen(5)
        client_socket, client_address = listen_socket.accept()
        newClientThread = Client_HandlerThread(client_socket, client_address)
        newClientThread.start()


# Setup Listening Socket
server_address = ('', LISTEN_PORT)
listen_socket = socket(AF_INET, SOCK_STREAM)
# listen_socket.setblocking(0)
listen_socket.bind(server_address)
q = queue.Queue()

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    run_program()