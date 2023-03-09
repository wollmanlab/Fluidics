
from Fluidics import *
from Pumps.SyringePump import SyringePump as Pump
from Protocols.SyringeProtocol import SyringeProtocol as Protocol
from Valves.ViciValve import ViciValve as Valve


class RamboFluidics(Fluidics):
    def __init__(self,verbose):
        super().__init__()
        self.Protocol = Protocol(verbose)
        self.Pump = Pump('COM11')
        self.Valve = Valve('COM1')
        hybe_valve = 3
        chamber_valve = 1
        self.Valve_Commands = {
                                'Valve3':{'valve':2,'port':1},
                                'Waste':{'valve':2,'port':10},
                                'Valve4':{'valve':2,'port':2},
                                'Valve1':{'valve':3,'port':1},
                                'TBS':{'valve':3,'port':2},
                                'IBuffer':{'valve':3,'port':2},
                                'WBuffer':{'valve':3,'port':3},
                                'TCEP':{'valve':3,'port':4},
                                'Hybe25':{'valve':3,'port':5},
                            }
        for i in range(1,25):
            self.Valve_Commands['Hybe'+str(i)] = {'valve':hybe_valve,'port':i}
            
        for i in range(6):
                self.Valve_Commands[chr(ord('A') + i)] = {'valve':chamber_valve,'port':i}

    