
from Fluidics import *
from Fluidics import Fluidics
from Pumps.SyringePump import SyringePump as Pump
from Protocols.SyringeProtocol import SyringeProtocol as Protocol
from Valves.ViciValve import ViciValve as Valve


class PurpleFluidics(Fluidics):
    def __init__(self,gui=False):
        super().__init__()  # call __init__ method of the super class
        self.verbose = True
        self.Protocol = Protocol(gui=gui)
        self.Pump = Pump('COM4',gui=gui)
        self.Valve = Valve('COM3',gui=gui)
        self.device = self.__class__.__name__
        self.Protocol.device = self.device
        self.Pump.device = self.device
        self.Valve.device = self.device
        self.Pump.wait_factor = 1/2
        self.Pump.speed_conversion = 1.9 #s/mL
        self.Protocol.speed = 1
        self.Protocol.closed_speed = 0.25
        self.Protocol.wait_factor = self.Pump.wait_factor
        self.Protocol.speed_conversion = self.Pump.speed_conversion
        self.Valve_Commands = {'TBS':{'valve':2,'port':6},
                                'IBuffer':{'valve':2,'port':9},
                                'WBuffer':{'valve':2,'port':7},
                                'TCEP':{'valve':2,'port':8},
                                'Waste':{'valve':3,'port':10},
                                'A':{'valve':3,'port':2},
                                'B':{'valve':3,'port':3},
                                'C':{'valve':3,'port':4},
                                'D':{'valve':3,'port':5},
                                'E':{'valve':3,'port':6},
                                'F':{'valve':3,'port':7},
                                'M':{'valve':3,'port':8},
                                'Hybe1':{'valve':1,'port':1},
                                'Hybe2':{'valve':1,'port':2},
                                'Hybe3':{'valve':1,'port':3},
                                'Hybe4':{'valve':1,'port':4},
                                'Hybe5':{'valve':1,'port':5},
                                'Hybe6':{'valve':1,'port':6},
                                'Hybe7':{'valve':1,'port':7},
                                'Hybe8':{'valve':1,'port':8},
                                'Hybe9':{'valve':1,'port':9},
                                'Hybe10':{'valve':1,'port':10},
                                'Hybe11':{'valve':1,'port':11},
                                'Hybe12':{'valve':1,'port':12},
                                'Hybe13':{'valve':1,'port':13},
                                'Hybe14':{'valve':1,'port':14},
                                'Hybe15':{'valve':1,'port':15},
                                'Hybe16':{'valve':1,'port':16},
                                'Hybe17':{'valve':1,'port':17},
                                'Hybe18':{'valve':1,'port':18},
                                'Hybe19':{'valve':1,'port':19},
                                'Hybe20':{'valve':1,'port':20},
                                'Hybe21':{'valve':1,'port':21},
                                'Hybe22':{'valve':1,'port':22},
                                'Hybe23':{'valve':1,'port':23},
                                'Hybe24':{'valve':1,'port':24},
                                'Hybe25':{'valve':2,'port':5},
                                'Valve1':{'valve':2,'port':10},
                                'Valve2':{'valve':3,'port':1}
                            }