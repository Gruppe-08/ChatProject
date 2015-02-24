# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
import json
import sys
import time

class Client:
    def __init__(self, host, server_port):
        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.receiver = MessageReceiver(self, self.connection)
        self.host = host
        self.server_port = server_port
        self.bottlesOfBeerOnTheWall = 99 # Arguably the most imporant variable
        self.shouldDisconnect = False # BeerBot never disconnects (willingly)
        self.run()

    def make_beer_lyric_1(self): # Arguably the most imporant method
        return ('{"request": "msg", "content": "' +
            str(self.bottlesOfBeerOnTheWall) + ' bottles of beer on the wall, ' +
            str(self.bottlesOfBeerOnTheWall) + ' bottles of beer.' +
            '"}')

    def make_beer_lyric_2(self): # Or maybe this one?
        self.bottlesOfBeerOnTheWall -= 1
        return ('{"request": "msg", "content": "' +
            'Take one down and pass it around, ' +
            str(self.bottlesOfBeerOnTheWall) +
            ' bottles of beer on the wall.'  +
            '"}')

    def make_beer_lyric_3(self):
        return ('{"request": "msg", "content": "' +
            'No more bottles of beer on the wall, no more bottles of beer.' +
            '"}')


    def make_beer_lyric_4(self):
        self.bottlesOfBeerOnTheWall = 99
        return ('{"request": "msg", "content": "' +
            'Go to the store and buy some more, 99 bottles of beer on the wall.' +
            '"}')


    def run(self):
        # Initiate the connection to the server
        try:
            self.connection.connect((self.host, self.server_port))
        except:
            print('Failed to connect to ' + self.host + ':' + str(self.server_port))
            return
        self.receiver.start() # Start receiver thread
        print('Connected to ' + self.host + ':' + str(self.server_port))
        self.send_payload('{"request": "login", "content": "BeerBot"}')
        time.sleep(1)
        self.send_payload('{"request": "msg", "content": "Never fear BeerBot is here!"}')
        time.sleep(1)
        # Loop until user requests to disconnect
        while True: # This is always true because there is no stopping the BeerBot
            time.sleep(3.7) # We must make sure everyone gets to enjoy every line of the song
            if(self.bottlesOfBeerOnTheWall != 0):
                self.send_payload(self.make_beer_lyric_1())
            else:
                self.send_payload(self.make_beer_lyric_3())
            time.sleep(3.7)
            if(self.bottlesOfBeerOnTheWall != 0):
                self.send_payload(self.make_beer_lyric_2())
            else:
                self.send_payload(self.make_beer_lyric_4())           


    def disconnect(self):
        pass # Why would you want to disconnect BeerBot :(

    def receive_message(self, message):
        pass # BeerBot doesn't give a shit what the users think

    def send_payload(self, data):
        self.connection.send(data) # Send json string directly


if __name__ == '__main__':
    # Take host and port from arguments if possible
    host = 'localhost'
    port = 9998
    if(len(sys.argv) > 1):
        host = sys.argv[1]
        if(len(sys.argv) > 2):
            port = int(sys.argv[2])
    client = Client(host, port)