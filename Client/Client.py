# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
import json

class Client:
    """
    This is the chat client class
    """

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.receiver = MessageReceiver(self, self.connection)
        self.host = host
        self.server_port = server_port

        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.host, self.server_port))
        self.receiver.start()
        print('Connected to ' + self.host + ':' + str(self.server_port))
        self.send_payload('{"request":"help", "content":""}')
        while True:
            command = raw_input()
            command = command.split(' ', 1)

            response = {}
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


    def disconnect(self):
        # TODO: Handle disconnection
        pass

    def receive_message(self, message):
        messages = message.split('}')
        for message in messages:
            if(message == ''):
                continue
            message += '}'
            message_json = json.loads(message)
            print(  message_json['timestamp'] + ' [' + message_json['sender'] + '] -> ' +
                    message_json['content'])

    def send_payload(self, data):
        self.connection.send(data)


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations is necessary
    """
    client = Client('localhost', 9998)
