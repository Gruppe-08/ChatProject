# -*- coding: utf-8 -*-
from threading import Thread

class MessageReceiver(Thread):
    def __init__(self, client, connection):
        super(MessageReceiver, self).__init__()
        
        # Flag to run thread as a deamon
        self.daemon = True

        self.client = client
        self.connection = connection

    def run(self):
        while not self.client.shouldDisconnect:
            received_string = self.connection.recv(4096)
            self.client.receive_message(received_string)
