
from Fluidics import *
from Fluidics import Fluidics
from Pumps.SyringePump import SyringePump as Pump
from Protocols.SyringeProtocol import SyringeProtocol as Protocol
from Valves.ViciValve import ViciValve as Valve


class NinjaFluidics(Fluidics):
    def __init__(self,gui=False):
        super().__init__()  # call __init__ method of the super class
        self.verbose = True
        self.Protocol = Protocol(gui=gui)
        self.Pump = Pump('COM6',gui=gui)
        self.Valve = Valve('COM7',gui=gui)
        self.Valve_Commands = {
                                'Waste':{'valve':4,'port':10},
                                'A':{'valve':4,'port':2},
                                'B':{'valve':4,'port':3},
                                'C':{'valve':4,'port':4},
                                'D':{'valve':4,'port':5},
                                'E':{'valve':4,'port':6},
                                'F':{'valve':4,'port':7},
                                'Air':{'valve':4,'port':8},
                                'Bypass':{'valve':4,'port':1},
                                'Valve3':{'valve':4,'port':1},
                                'Hybe1':{'valve':2,'port':1},
                                'Hybe2':{'valve':2,'port':2},
                                'Hybe3':{'valve':2,'port':3},
                                'Hybe4':{'valve':2,'port':4},
                                'Hybe5':{'valve':2,'port':5},
                                'Hybe6':{'valve':2,'port':6},
                                'Hybe7':{'valve':2,'port':7},
                                'Hybe8':{'valve':2,'port':8},
                                'Hybe9':{'valve':2,'port':9},
                                'Hybe10':{'valve':2,'port':10},
                                'Hybe11':{'valve':2,'port':11},
                                'Hybe12':{'valve':2,'port':12},
                                'Hybe13':{'valve':2,'port':13},
                                'Hybe14':{'valve':2,'port':14},
                                'Hybe15':{'valve':2,'port':15},
                                'Hybe16':{'valve':2,'port':16},
                                'Hybe17':{'valve':2,'port':17},
                                'Hybe18':{'valve':2,'port':18},
                                'Hybe19':{'valve':2,'port':19},
                                'Hybe20':{'valve':2,'port':20},
                                'Hybe21':{'valve':2,'port':21},
                                'Hybe22':{'valve':2,'port':22},
                                'Hybe23':{'valve':2,'port':23},
                                'Hybe24':{'valve':2,'port':24},
                                'Hybe25':{'valve':3,'port':5},
                                'TBS':{'valve':3,'port':6},
                                'IBuffer':{'valve':3,'port':6},
                                'WBuffer':{'valve':3,'port':7},
                                'TCEP':{'valve':3,'port':8},
                                'Valve2':{'valve':3,'port':10}
                            }
    