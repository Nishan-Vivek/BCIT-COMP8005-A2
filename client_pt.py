import socket
import sys
from multiprocessing import Pool
import threading

SERVER_PORT = 10000
SERVER_ADDRESS = 'localhost'
PROC_NUM = 4
THREAD_PER_PROC = 500
REPEAT = 0

def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)

def messaging(sock, message):
    print('sending "%s"' % message)
    sock.sendall(message.encode())
    # amount_received = 0
    # amount_expected = len(message)
    # while amount_received < amount_expected:
    data = sock.recv(1024).decode()
    # amount_received += len(data)
    print('received "%s"' % data);


class ClientThread(threading.Thread):
    def __init__(self, server_address):
        threading.Thread.__init__(self)
        self.server_address = server_address

    def run(self):
        #Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print_d('connecting to %s port %s' % self.server_address)
        sock.connect(self.server_address)
        try:
            message = "This is the message.  It will be repeated."
            if REPEAT == 0:
                while 1:
                    messaging(sock, message)
            else:
                for x in range(REPEAT):
                    messaging(sock, message)
        except Exception:
            print_d("Thread encountered exception")
            sock.close()
        finally:
            sock.close()

        print_d("Ending Thread")

def client_process(*args):
    threads = []
    server_address = (sys.argv[1], 10000)

    for _ in range (THREAD_PER_PROC):
        threads.append(ClientThread(server_address))

    [x.start() for x in threads]
    [x.join() for x in threads]
    print_d("Ending Process")

if __name__ == '__main__':
    pool = Pool(processes=PROC_NUM)
    results = pool.map(client_process, [None for _ in range(PROC_NUM)])