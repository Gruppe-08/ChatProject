# -*- coding: utf-8 -*-
import SocketServer
import json
from datetime import datetime

logged_in_users = {} # Hashmap with username as key and socket as value
history = []

class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def send_message(self, socket, message):
        try:
            socket.send(message)
        except:
            self.connectionBroken = True

    def login(self, socket, username):
        global logged_in_users
        global history

        # Check that the user isn't logged in already with a different account
        if(self.username != None):
            self.send_server_message(socket, 'error', 'You are already logged in')
            return

        # Check that the username isn't already in use
        if(username not in logged_in_users):
            logged_in_users[username] = socket
            self.username = username
            for message in history:
                self.send_message(socket, message)

            # Broadcast logged in message to all users
            response = self.make_response('Server', 'info', (self.username + ' signed in'))
            self.broadcast_message(response)
            print('User \'' + self.username + '\' connected')
        else:
            self.send_server_message(socket, 'error', 'Username "' + username + '" already taken')

    def logout(self, socket):
        response = self.make_response('Server', 'info', (self.username + ' signed out'))
        self.broadcast_message(response)
        self.connectionBroken = True

    def help(self, socket):
        help_message = ('login <username> - Log onto the server with given username \n' +
            'logout - Log out of the server\n' +
            'msg <message> - Send a message to other logged in members\n' +
            'names - List all logged in users\n' +
            'help - View this text"')
        self.send_server_message(socket, 'info', help_message)

    def msg(self, socket, message):
        if(self.username == None):
            self.send_server_message(socket, 'error', 'You cannot send messages when not logged in')
            return
        response = self.make_response(self.username, 'message', message)
        self.broadcast_message(response)
        # Append message to history log
        history.append(self.make_response(self.username, 'history', message))
        print('User \'' + self.username + '\' said: ' + message)

    def names(self, socket):
        global logged_in_users

        if(self.username == None):
            self.send_server_message(socket, 'error', 'You must be logged in to do this')
            return

        name_string  = ''
        for user in logged_in_users:
            name_string += user + ', '
        if(len(logged_in_users) > 0):
            name_string = name_string[:-2]
        self.send_server_message(socket, 'info', name_string)

    def broadcast_message(self, response):
        for iter_username, iter_socket in logged_in_users.items():
            self.send_message(iter_socket, response)

    def send_server_message(self, socket, response_type,  message):
        response = self.make_response('Server', response_type, message)
        self.send_message(socket, response)

    def make_response(self, sender, response_type, content):
        response = {
            'timestamp': datetime.now().strftime('%d.%M.%Y %H:%M'), # Use DD.MM.YY HH:MM timestamp format
            'sender': sender,
            'response': response_type,
            'content': content }
        return json.dumps(response)

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.connectionBroken = False
        self.username = None
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        # Loop that listens for messages from the client
        while not self.connectionBroken:
            try:
                received_string = self.connection.recv(4096).rstrip()
            except:
                pass
            # Deserialize recieved
            received_json = 0
            try:
                received_json = json.loads(received_string)
                # Check that the sent request contains required fields
                if(     'request' not in received_json or
                        'content' not in received_json):
                    raise ValueError
            except:
                # Send error if malformed request sent
                self.send_server_message(self.request, 'Error', 'Invalid request format')
                continue

            #Process request
            request_type = received_json['request']
            if(request_type == 'login'):
                self.login(self.request, received_json['content'])
            elif(request_type == 'logout'):
                self.logout(self.request)
                break # Break loop and thus end connection
            elif(request_type == 'help'):
                self.help(self.request)
            elif(request_type == 'msg'):
                self.msg(self.request, received_json['content'])
            elif(request_type == 'names'):
                self.names(self.request)
        # Connection terminated
        if(self.username != None):
            print('User \'' + self.username + '\' disconnected')
            del logged_in_users[self.username]

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations is necessary
    """
    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations is necessary
    """
    HOST, PORT = 'localhost', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()