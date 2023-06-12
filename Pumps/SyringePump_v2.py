from Pumps.Pump import *
from fractions import Fraction
import numpy as np
class SyringePump_v2(Pump):
    """
    """
    def __init__(self,com_port,forward=5,reverse=4,gui=False):
        super().__init__()
        self.forward = 5
        self.reverse = 4
        self.com_port = com_port
        self.speed_conversion = 1.9*(5/4) # mL/s
        self.wait_factor = 1/3
        if not gui:
            self.serial = serial.Serial(com_port, 9600, timeout=2)

    def flow(self,volume):
        if self.direction=='Forward':
            direction = 'F'
        elif self.direction=='Reverse':
            direction = 'R'
        else:
            direction = 'U' 

        duration = (float(volume)/float(self.speed))*self.speed_conversion

        #  // Format is @{direction}%{speed}_{duration}$!
        message = bytes("@{direction}%{speed}_{duration}$!".format(direction=direction, speed=self.speed,duration=duration), 'utf-8')
        # print(message)
        try:
            self.serial.write(message)
            self.serial.flush()
        except Exception as e:
            self.update_user(e)
            self.update_user('Failed to set pin.')
            pass
        
        precise_sleep(1)

        #  // Format is @{direction}%{speed}_{duration}$!
        message = bytes("@{direction}%{speed}_{duration}$!".format(direction='U', speed=self.speed,duration=duration), 'utf-8')
        print(message)
        try:
            self.serial.write(message)
            self.serial.flush()
        except Exception as e:
            self.update_user(e)
            self.update_user('Failed to set pin.')
            pass

        precise_sleep(duration+(float(volume)*self.speed_conversion)*self.wait_factor)


