from Pumps.Pump import *
from fractions import Fraction
import numpy as np
class SyringePump_v2(Pump):
    """
    Definition of SyringePump, a subclass of Pump.
    """
    def __init__(self,com_port,forward=5,reverse=4,gui=False):
        super().__init__()
        self.forward = 5
        self.reverse = 4
        self.com_port = com_port
        # speed_conversion is mesaured by recording the time (seconds) the syringe pump takes to withdraw 1mL of water.
        # This value varies from pump to pump and must be mesaured for each new syringe pump.
        self.speed_conversion = 1.9*(5/4) # in the unit of sec/mL
        # wait_factor is for determining the extra amount of time to wait in addition to the theoretical duration.
        # The formual is: total_waiting = theoretical_duration+wait_factor*(volume*speed_conversion)
        self.wait_factor = 1/3
        if not gui:
            self.serial = serial.Serial(com_port, 9600, timeout=2)
    
    # self.flow is for 'flowing' user specified amount of liquid in user specified direction.
    # It translates user specification into a formatted serial message and write to Arduino.
    def flow(self,volume):
        # Abbreviate direction to minimize RAM usage on Arduino
        if self.direction=='Forward':
            direction = 'F'
        elif self.direction=='Reverse':
            direction = 'R'
        else:
            direction = 'U' 
            
        # Calculate the theoretical duration for the syringe pump to finish pumping.
        # Note that the speed here is actually duty cycle.
        duration = (float(volume)/float(self.speed))*self.speed_conversion

        # Translate user specification in to formatted message for Arduino. The format is @{direction}%{speed}_{duration}$!
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

        # Send another message following the first message for stopping the syringe pump after finishing the job specified in the first message.
        message = bytes("@{direction}%{speed}_{duration}$!".format(direction='U', speed=self.speed,duration=duration), 'utf-8')
        print(message)
        try:
            self.serial.write(message)
            self.serial.flush()
        except Exception as e:
            self.update_user(e)
            self.update_user('Failed to set pin.')
            pass

        # Sleep for the theoretical duration plus some extra amount of buffer to ensure no further action before the syringe pump finishes the current job.
        precise_sleep(duration+(float(volume)*self.speed_conversion)*self.wait_factor)


