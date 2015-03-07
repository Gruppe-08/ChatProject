# Simple Chat Server/Client
This is a simple Chat Server/Client for NTNU course TTM4100 - Communication Services and Networks.

The server application is a simple, threaded chat server that uses TCP connections to communicate with a series of users that have logged in through a client application.

The client application is a simple console application that establishes a connection to a server and allows the user to send and receive messages from and to other users on the same server.

## How to debug without working client
Install telnet and connect with host and port number ie. "telnet localhost 9998"
Now you can write requests manually ie. {"request":"login", "content":"myusername"}
and see the responses
