import serial
import time
from fileu import *
class Pump:
    """
    Definition of the superclass Pump.
    """
    def __init__(self,gui=False):
        self.verbose=True # When in verbose mode, update_user() will record the input message to the log. 
        self.direction = 'Forward'
        self.volume = 0 # In the unit of mL
        self.speed = 0 # In the unit of mL/sec
        
    # self.update_user() is for writing messages to the log 
    def update_user(self,message,level=20,logger='Pump'):
        logger = self.device +'***' + logger
        if self.verbose:
            update_user(message,level=level,logger=logger) # This is the update_user defined in fileu.

    # self.start_flow() starts a 'flow' of liquid from the pump in user specified volume, direction and speed
    def start_flow(self,volume,direction,speed):
        self.set_direction(direction)
        self.set_speed(speed)
        self.flow(volume)
    
    # self.set_direction() is for setting the direction of the pump.
    def set_direction(self,direction):
        self.direction = direction

    # self.set_speed() is for setting the speed of the pump.
    def set_speed(self,speed):
        self.speed = speed
    
    # self.flow() needs to be overwritten (defined) when defining a subclass for specific type of pump
    def flow(self,volume):
        """ OVERWRITE"""

        


    


    


