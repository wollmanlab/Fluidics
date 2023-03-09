import serial
import time
from fileu import update_user
class Valve:
    """

    """
    def __init__(self):
        self.verbose=True
        self.current_port = {}

    def notify_user(self,message,level=20):
        if self.verbose:
            update_user(message,level=level,logger=None)

    def set_port(self,valve,port):
        self.current_port[valve] = port

    def get_port(self,valve):
        return self.current_port[valve]


    


    


