
from Fluidics import *
from Fluidics import Fluidics
from Pumps.SyringePump import SyringePump as Pump
from Protocols.SyringeProtocol import SyringeProtocol as Protocol
from Valves.ViciValve import ViciValve as Valve


class RamboFluidics(Fluidics):
    def __init__(self,gui=False):
        super().__init__()  # call __init__ method of the super class
        self.verbose = True
        self.Protocol = Protocol(gui=gui)
        self.Pump = Pump('COM11',gui=gui)
        self.Valve = Valve('COM1',gui=gui)
        hybe_valve = 2
        chamber_valve = 1
        self.Valve_Commands = {
                                'Valve2':{'valve':1,'port':16},
                                'Waste':{'valve':1,'port':15},
                                'TBS':{'valve':1,'port':14},
                                'WBuffer':{'valve':1,'port':13},
                                'TCEP':{'valve':1,'port':12},
                                'Hybe25':{'valve':1,'port':11},
                            }
        for i in range(1,25):
            self.Valve_Commands['Hybe'+str(i)] = {'valve':hybe_valve,'port':i}
            
        for i in range(6):
                self.Valve_Commands[chr(ord('A') + i)] = {'valve':chamber_valve,'port':i+1}

    