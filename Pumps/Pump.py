import serial
import time
from fileu import *
class Pump:
    """

    """
    def __init__(self,gui=False):
        self.verbose=True
        self.direction = 'Forward'
        self.volume = 0
        self.speed = 0

    def update_user(self,message,level=20,logger='Pump'):
        logger = self.device +'***' + logger
        if self.verbose:
            update_user(message,level=level,logger=logger)

    def start_flow(self,volume,direction,speed):
        self.set_direction(direction)
        self.set_speed(speed)
        self.flow(volume)

    def set_direction(self,direction):
        self.direction = direction

    def set_speed(self,speed):
        self.speed = speed

    def flow(self,volume):
        """ OVERWRITE"""

        


    


    


