import select
from socket import *
import sys
import queue


def print_d(message, debug=True):
    """Prints message if debug is true."""
    if debug:
        print(message, file=sys.stderr)


server_address = ('', 10000)
listen_socket = socket(AF_INET, SOCK_STREAM)
listen_socket.setblocking(0)
listen_socket.bind(server_address)
listen_socket.listen(5)

# Sockets from which we expect to read
inputs = [listen_socket]

# Sockets to which we expect to write
outputs = []

# Outgoing message queues (socket:Queue)
message_queues = {}

while inputs:
    # Wait for at least one of the sockets to be ready for processing
    print_d('\nwaiting for the next event')
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for s in readable:

        if s is listen_socket:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            print_d('...connected from:' + str(client_address), True)
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data we want to send
            message_queues[connection] = queue.Queue()

        else:
            data = s.recv(1024)
            if data:
                # A readable client socket has data
                # print >>sys.stderr, 'received "%s" from %s' % (data, s.getpeername()) <<<<<<< switch to puthon3.4 and determine if needed
                message_queues[s].put(data)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)

                else:
                    data = s.recv(1024)
                    if data:
                        # A readable client socket has data
                        #                        print output here maybe
                        message_queues[s].put(data)
                        # Add output channel for response
                        if s not in outputs:
                            outputs.append(s)
                        else:
                            # Interpret empty result as closed connection
                            #                           maybe put print out here
                            if s in outputs:
                                outputs.remove(s)
                            inputs.remove(s)
                            s.close()

                            #                             Remove message queue
                            del message_queues[s]

                            # handle outputs
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except queue.Empty:
            # NO messages waiting so stop checking writeablelity
            outputs.remove(s)
        else:
            # print output line maaybe
            s.send(next_msg)
