import serial
import time
from fileu import *
class Valve:
    """

    """
    def __init__(self,gui=False):
        self.verbose=True
        self.current_port = {}

    def update_user(self,message,level=20,logger='Valve'):
        if self.verbose:
            update_user(message,level=level,logger=logger)

    def set_port(self,valve,port):
        self.current_port[valve] = port

    def get_port(self,valve):
        return self.current_port[valve]


    


    


