
from Fluidics import *
from Fluidics import Fluidics
# from Pumps.SyringePump import SyringePump as Pump
# from Protocols.SyringeProtocol import SyringeProtocol as Protocol
# from Valves.ViciValve import ViciValve as Valve


class SamplePrepFluidics(Fluidics):
    def __init__(self,gui=False):
        super().__init__()  # call __init__ method of the super class
        self.verbose = True
        Protocol = getattr(importlib.import_module('SyringeProtocol'), 'SyringeProtocol')
        Pump = getattr(importlib.import_module('SyringePump'), 'SyringePump')
        Valve = getattr(importlib.import_module('ViciValve'), 'ViciValve')
        self.Protocol = Protocol(gui=gui)
        self.Pump = Pump('/dev/ttyACM0',gui=gui)
        self.Valve = Valve('/dev/ttyUSB0',gui=gui)
        self.Pump.wait_factor = 1/2
        self.Pump.speed_conversion = 1.9
        self.Protocol.speed = 1
        self.Protocol.closed_speed = 0.25
        self.Protocol.wait_factor = self.Pump.wait_factor
        self.Protocol.speed_conversion = self.Pump.speed_conversion
        self.Protocol.rinse_volume = 2.5

        chamber_valve = 1
        self.Valve_Commands = {
                                'Waste':{'valve':1,'port':13},
                                'TBS':{'valve':1,'port':24},
                                'PBS':{'valve':1,'port':23},
                                'MOPS':{'valve':1,'port':22},
                                'TPERM':{'valve':1,'port':21},
                                'Formamide':{'valve':1,'port':20},
                                'EthyleneCarbonate':{'valve':1,'port':19},
                                'ProtKSDS':{'valve':1,'port':18},
                                'ProtK':{'valve':1,'port':17},
                                'MelphaX':{'valve':1,'port':16},
                            }
        for i in range(6):
                self.Valve_Commands[chr(ord('A') + i)] = {'valve':chamber_valve,'port':i+1}





    