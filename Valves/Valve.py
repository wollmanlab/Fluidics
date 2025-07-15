import serial
import time
from fileu import *
class Valve:
    """
    Definition of the superclass Valve.
    """
    def __init__(self,gui=False):
        self.verbose=True # When in verbose mode, update_user() will record the input message to the log.
        self.current_port = {} # A dictionary for storing the currently selected port of each valve.
        
    # self.update_user() is for writing messages to the log
    def update_user(self,message,level=20,logger='Valve'):
        logger = self.device +'***' + logger
        if self.verbose:
            update_user(message,level=level,logger=logger)
    
    # self.set_port() is for selecting the specified port of the specified valve.
    def set_port(self,valve,port):
        self.current_port[valve] = port

    # self.get_port() is for getting the currently selected port of the specified valve. 
    def get_port(self,valve):
        return self.current_port[valve]


    


    


