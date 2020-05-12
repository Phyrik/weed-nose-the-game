import socket
import sys
import time

class Socket:
    def __init__(self, host, ip, port):
        self.port = port
        self.ip = ip
        self.host = host
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.host == True:
            self.s.bind((self.ip, self.port))
        if self.host == False:
            self.s.settimeout(5)
            try:
                self.s.connect((self.ip, self.port))
            except socket.timeout:
                print("Connection timed out. Exiting the game.")
                time.sleep(2)
                sys.exit()
            s.settimeout(None)