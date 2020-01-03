# BCIT COMP8005 Assignment 1 - Select, multi-threaded, and epoll-based client-server implementations

## Objective 

To compare the scalability and performance of the select-, multi-threaded-, and epoll-based client-server implementations.

## Program Descriptions

### Threaded Server

The multi-threaded server follows a basic design. The main processes listen on the server socket for incoming connections. On receiving the connection, a client socket is created and passed to a spawned thread for handling. The client handling thread then performs the echo with the client until the client terminates the connection or an error has occurred. It then closes the connection and publishes its recorded connection statistics back to the main process. The main processes will run indefinitely until the user terminates the program with Ctrl-C. It then gathers and writes the recorded connection statistics to a csv file. 

### Select Server

This server utilizes the Select() function for asynchronous socket handling in a single thread. The main sever socket is created and added to the list of sockets that select will monitor. In the main loop select is called against the socket list. If the server socket is ready to read due to a client connection a client socket is created and added to the socket list. The Select() statement is run again against the list. As sockets are ready for reading, writing or have an error detected they are put into corresponding socket lists/sets. The main loop then goes through the lists reading from the read list and writing to the sockets in the write list. If the socket is in the error/exception list, the socket is closed and removed from the main socket list. Statistics are gathered on socket reads and are complied and written to disk on server termination. 

### Epol Server

The epoll server is similar to the select server but instead uses the epoll() function in edge-triggered mode. On before the main loop the server socket is registered with the epoll object to trigger events on EPOLLIN (ready to read). The main loop is then started. When epoll() detects the server socket has received a connection its FD is added to the event list. The main loop then checks all the events that have the EPOLLIN flag set, if it is the server socket is knows a client connection was made and creates a new client socket. This client socket is then registered with EPOLLIN. The loop processes EPOLLIN events and EPOLLOUT events in that order. When a client connection is ready to read its messaged is stored and the socket then registered with EPOLLOUT. When the EPOLLOUT section of the loop is reached the message is echoed back to the client. Both sections of the loop handle will also close and unregister the socket when appropriate. Upon program termination the connection statistics are compiled and written to a csv file. 



#TODO: Find original docs and submitted files.