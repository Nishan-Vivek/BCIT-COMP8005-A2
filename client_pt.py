import socket
import sys
from multiprocessing import Pool, Process
import threading
import os

DEBUG = False
SERVER_PORT = 10000
SERVER_ADDRESS = 'localhost'
PROC_NUM = 1000
THREAD_PER_PROC = 1
REPEAT = 1000
SOCKET_TIMEOUT = 10
PAYLOAD = "This is the payload"


def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)


def getClientID():
    return "PID:{0}".format(os.getpid()) + "-" + threading.current_thread().getName()

def messaging2(sock, message):
    stats = ClientStats()
    stats.client_id = getClientID()
    stats.req_w = REPEAT
    stats.req_c = 0
    stats.data_transferred = 0

    try:

        for x in range(REPEAT):
            print_d('sending "%s"' % message, DEBUG)
            sock.sendall(message.encode())
            data = sock.recv(1024).decode()
            if data:
                stats.req_c +=1
                stats.data_transferred += sys.getsizeof(data)
                print_d('received "%s"' % data, DEBUG)
    except:
        return stats
        raise
    finally:
        return stats


def messaging(sock, message):
    try:
        print_d('sending "%s"' % message, DEBUG)
        sock.sendall(message.encode())
        data = sock.recv(1024).decode()
        print_d('received "%s"' % data, DEBUG);
    except:
        raise

class ClientStats():
    def __init__(self, client_id, req_c, req_w, avg_rtt, data_sent):
        self.client_id = client_id
        self.req_c = req_c
        self.req_w = req_w
        self.data_sent = data_sent
        self.avg_rtt = avg_rtt


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
            sock.connect(self.server_address)
            message = PAYLOAD

            #Send the payload the REPEAT number of times or indefitealy if REPEAT = 0
            if REPEAT == 0:
                while 1:
                    messaging(sock, message)
            else:
                for x in range(REPEAT):
                    messaging(sock, message)

        #close sockets on exceptions and completion
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
    results = pool.map(client_process, range(PROC_NUM))
    pool.close()
    pool.join()
    print_d("All processes ended")
