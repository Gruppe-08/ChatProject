# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
import json
import sys

class Client:
    def __init__(self, host, server_port):
        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.receiver = MessageReceiver(self, self.connection)
        self.host = host
        self.server_port = server_port

        self.run()

    def run(self):
        # Initiate the connection to the server
        try:
            self.connection.connect((self.host, self.server_port))
        except:
            print('Failed to connect to ' + self.host + ':' + str(self.server_port))
            return
        self.receiver.start() # Start receiver thread
        print('Connected to ' + self.host + ':' + str(self.server_port))

        # Loop until user requests to disconnect
        while True:
            command = raw_input()
            command = command.split(' ', 1)

            response = {} # Empty json object
            response['request'] = command[0]
            if(len(command) != 1):
                response['content'] = command[1]
            else:
                response['content'] = None
            try:
                self.send_payload(json.dumps(response))
            except Exception as e:
                print(e)
                print('Invalid command syntax')

        self.disconnect() # Disconnect before terminating program

    def disconnect(self):
        self.connection.close() # Close the socket before terminating

    def receive_message(self, message):
        # Handle cases where TCP responses were concatenated
        messages = message.split('}')
        for message in messages:
            if(message == ''):
                continue
            message += '}'
            message_json = json.loads(message)
            print(  message_json['timestamp'] + ' [' + message_json['sender'] + '] -> ' +
                    message_json['content'])

    def send_payload(self, data):
        self.connection.send(data) # Send json string directly


if __name__ == '__main__':
    # Take host and port from arguments if possible
    host = '192.168.1.13'
    port = 9998
    if(len(sys.argv) > 1):
        host = sys.argv[1]
        if(len(sys.argv) > 2):
            port = int(sys.argv[2])
    client = Client(host, port)