
from Fluidics import *
from Fluidics import Fluidics
# from Pumps.SyringePump import SyringePump as Pump
# from Protocols.SyringeProtocol import SyringeProtocol as Protocol
# from Valves.ViciValve import ViciValve as Valve


class GreenSamplePrep(Fluidics):
    def __init__(self,gui=False):
        super().__init__()  # call __init__ method of the super class
        self.verbose = True
        Protocol = getattr(importlib.import_module('SyringeProtocol'), 'SyringeProtocol')
        # Pump = getattr(importlib.import_module('SyringePump'), 'SyringePump')
        Pump = getattr(importlib.import_module('SyringePump_v2'), 'SyringePump_v2')
        Valve = getattr(importlib.import_module('ViciValve'), 'ViciValve')
        self.Protocol = Protocol(gui=gui)
        self.Pump = Pump('COM4',gui=gui)
        self.Valve = Valve('COM8',gui=gui)
        self.device = self.__class__.__name__
        self.Protocol.device = self.device
        self.Pump.device = self.device
        self.Valve.device = self.device
        self.Pump.wait_factor = 1/2
        self.Pump.speed_conversion = 1.9*(5/4)
        self.Protocol.speed = 0.5
        self.Protocol.max_speed = 0.5
        self.Protocol.closed_speed = 0.25
        self.Protocol.wait_factor = self.Pump.wait_factor
        self.Protocol.speed_conversion = self.Pump.speed_conversion
        self.Protocol.rinse_volume = 2

        self.Valve_Commands = {
                                'A':{'valve':1,'port':1},
                                'B':{'valve':1,'port':2},
                                'C':{'valve':1,'port':3},
                                'D':{'valve':1,'port':4},
                                'E':{'valve':1,'port':5},
                                'F':{'valve':1,'port':6},
                                'G':{'valve':1,'port':7},
                                'H':{'valve':1,'port':8},
                                'I':{'valve':1,'port':9},
                                'J':{'valve':1,'port':10},
                                'K':{'valve':1,'port':11},
                                'L':{'valve':1,'port':12},
                                'TBS':{'valve':1,'port':13},
                                'PBS':{'valve':1,'port':14},
                                'MOPS':{'valve':1,'port':15},
                                'TPERM':{'valve':1,'port':16},
                                'WBuffer':{'valve':1,'port':17},
                                'Gel':{'valve':1,'port':18},
                                'ProtK':{'valve':1,'port':19},
                                'MelphaX':{'valve':1,'port':20},
                                'Ethanol':{'valve':1,'port':21},
                                'Bleach':{'valve':1,'port':22},
                                'Air':{'valve':1,'port':23},
                                'Waste':{'valve':1,'port':24},
                            }
        





    