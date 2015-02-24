# -*- coding: utf-8 -*-
import SocketServer
import json
from datetime import datetime

loggedInUsers = {} # Hashmap with username as key and socket as value
history = []

class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def login(self, socket, username):
        global loggedInUsers
        global history

        # Check that the user isn't logged in already with a different account
        for cur_username, cur_socket in loggedInUsers.items():
            if(socket == cur_socket):
                # Inform user that he can only log in with one user
                self.sendServerMessage(socket, 'error', 'You are already logged in as ' + username)
                return
        
        #Check that the username isn't already in use
        if(username not in loggedInUsers):
            loggedInUsers[username] = socket
            self.sendServerMessage(socket, 'info', 'Successfully logged in as ' + username)
            for message in history:
                socket.sendall(message)
        else:
            self.sendServerMessage(socket, 'error', 'User "' + username + '" already logged in')

    def username_from_socket(self, socket):
        global loggedInUsers
        for username, socket in loggedInUsers.items():
            if(socket == socket):
                return username
        else:
            return False
    def logout(self, socket):
        global loggedInUsers
        
        # Look for user with same socket in usermapping
        username = self.username_from_socket(socket)
        if(username == False):
            self.sendServerMessage(socket, 'info', 'Goodbye') # User wasn't logged in yet
            return

        # Found user, remove from usermapping
        del loggedInUsers[username]
        self.sendServerMessage(socket, 'info', 'Goodbye ' + username)

    def help(self, socket):
        help_message = "Welcome to group 8's chat server! Valid commands are: \n\
        login <username> - Log onto the server with given username \n\
        logout - Log out of the server\n\
        msg <message> - Send a message to other logged in members\n\
        names - List all logged in users\n\
        help - View this text"
        self.sendServerMessage(socket, 'info', help_message)

    def msg(self, socket, message):
        sender = self.username_from_socket(socket)
        if(sender == False):
            self.sendServerMessage(socket, 'error', 'You cannot send messages when not logged in')
            return
        response = self.makeResponse(sender, 'message', message)
        for username, socket in loggedInUsers.items():
            socket.sendall(response)
        # Append message to history log
        history.append(self.makeResponse(sender, 'history', message))




    def sendServerMessage(self, socket, response_type,  message):
        response = self.makeResponse('Server', response_type, message)
        socket.sendall(response)

    def makeResponse(self, sender,response_type, content, time=datetime.now()):
        response = {
            'timestamp': time.strftime('%d.%M.%Y %H:%M'), # Use DD.MM.YY HH:MM timestamp format
            'sender': sender,
            'response': response_type,
            'content': content }
        return json.dumps(response)

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096).rstrip()
            # Deserialize recieved
            received_json = 0
            try:
                print("'" + received_string + "'")
                received_json = json.loads(received_string)
                # Check that the sent request contains required fields
                if(     'request' not in received_json or
                        'content' not in received_json):
                    raise ValueError
            except Exception as e:
                print(e)
                # Send error if malformed request sent
                self.sendServerMessage(self.request, 'Error', 'Invalid request format')
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
