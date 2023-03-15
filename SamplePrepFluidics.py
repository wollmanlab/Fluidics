
from Fluidics import *
from Fluidics import Fluidics
from Pumps.SyringePump import SyringePump as Pump
from Protocols.SyringeProtocol import SyringeProtocol as Protocol
from Valves.ViciValve import ViciValve as Valve


class SamplePrepFluidics(Fluidics):
    def __init__(self, verbose):
        super().__init__()  # call __init__ method of the super class
        self.verbose = verbose
        self.Protocol = Protocol(verbose)
        self.Pump = Pump('/dev/ttyACM0')
        self.Valve = Valve('/dev/ttyUSB0')
        chamber_valve = 1
        self.Valve_Commands = {
                                'Waste':{'valve':1,'port':13},
                                'TBS':{'valve':1,'port':14},
                                'Urea':{'valve':1,'port':15},
                                'SDS':{'valve':1,'port':16},
                                'TCEP':{'valve':1,'port':23},
                                'ProtK':{'valve':1,'port':24},
                            }
        for i in range(4):
                self.Valve_Commands[chr(ord('A') + i)] = {'valve':chamber_valve,'port':i+1}


    