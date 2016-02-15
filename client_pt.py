import socket
import sys
from multiprocessing import Pool
import threading
import os

DEBUG = False
SERVER_PORT = 10000
SERVER_ADDRESS = 'localhost'
PROC_NUM = 6
THREAD_PER_PROC = 1000
REPEAT = 100
SOCKET_TIMEOUT = 0


def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)


def messaging(sock, message):
    try:
        print_d('sending "%s"' % message, DEBUG)
        sock.sendall(message.encode())
        data = sock.recv(1024).decode()
        print_d('received "%s"' % data, DEBUG);
    except:
        raise


class ClientThread(threading.Thread):
    def __init__(self, server_address):
        threading.Thread.__init__(self)
        self.server_address = server_address

    def run(self):

        try:
            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if SOCKET_TIMEOUT != 0:
                sock.settimeout(SOCKET_TIMEOUT)
            print_d("PID:{0}".format(
                os.getpid()) + "-" + threading.current_thread().getName() + ' connecting to %s port %s ' % self.server_address)
            # print_d('connecting to %s port %s ' % self.server_address + "with PID:{0}".format(os.getpid()) + "-" + threading.current_thread().getName())
            sock.connect(self.server_address)
            message = "This is the message.  It will be repeated."
            if REPEAT == 0:
                while 1:
                    messaging(sock, message)
            else:
                for x in range(REPEAT):
                    messaging(sock, message)
        except Exception as e:
            print_d(
                "PID:{0}".format(os.getpid()) + "-" + threading.current_thread().getName() + " encountered " + repr(e))
            sock.close()
        finally:
            sock.close()

        print_d("PID:{0}".format(os.getpid()) + "-" + threading.current_thread().getName() + " ending Thread")


def client_process(*args):
    print_d("PID:{0}".format(os.getpid()) + " created.")
    threads = []
    server_address = (sys.argv[1], 10000)

    for _ in range(THREAD_PER_PROC):
        threads.append(ClientThread(server_address))

    [x.start() for x in threads]
    [x.join() for x in threads]
    print_d("PID:{0}".format(os.getpid()) + " Ending Process")


if __name__ == '__main__':
    pool = Pool(processes=PROC_NUM)
    results = pool.map(client_process, [None for _ in range(PROC_NUM)])
