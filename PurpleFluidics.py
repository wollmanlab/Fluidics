
from Fluidics import *
from Fluidics import Fluidics


class PurpleFluidics(Fluidics):
    def __init__(self,gui=False):
        super().__init__()  # call __init__ method of the super class
        self.verbose = True
        Protocol = getattr(importlib.import_module('SyringeProtocol'), 'SyringeProtocol')
        Pump = getattr(importlib.import_module('SyringePump_v2'), 'SyringePump_v2')
        Valve = getattr(importlib.import_module('ViciValve'), 'ViciValve')
        self.Protocol = Protocol(gui=gui)
        self.Pump = Pump('COM4',gui=gui)
        self.Valve = Valve('COM3',gui=gui)
        self.device = self.__class__.__name__
        self.Protocol.device = self.device
        self.Pump.device = self.device
        self.Valve.device = self.device
        self.Pump.wait_factor = 1/2
        self.Pump.speed_conversion = 1.9*(5/4) #s/mL

        self.Protocol.speed = 0.5#1
        self.Protocol.max_speed = 0.5#1
        self.Protocol.mixes = 0#3

        self.Protocol.closed_speed = 0.25
        self.Protocol.wait_factor = self.Pump.wait_factor
        self.Protocol.speed_conversion = self.Pump.speed_conversion
        self.Protocol.chamber_volume = 5
        self.Protocol.rinse_volume = 2
        self.Protocol.hybe_volume = 2
        self.Protocol.rinse_time = 2.5*60
        self.Protocol.hybe_time = 30*60
        self.Protocol.prime_volume = 3
        self.Protocol.vacume = True
        self.Valve_Commands = {'Dapi':{'valve':3,'port':2},
                                'TBS':{'valve':3,'port':6},
                               'HybeTBS':{'valve':3,'port':6},
                               'StripTBS':{'valve':3,'port':9},
                                'IBuffer':{'valve':3,'port':9},
                                'WBuffer':{'valve':3,'port':7},
                                'TCEP':{'valve':3,'port':8},
                                'Waste':{'valve':4,'port':10},
                                'A':{'valve':4,'port':2},
                                'B':{'valve':4,'port':3},
                                'C':{'valve':4,'port':4},
                                'D':{'valve':4,'port':5},
                                'E':{'valve':4,'port':6},
                                'F':{'valve':4,'port':7},
                                'Air':{'valve':4,'port':9},
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
                                'Hybe26':{'valve':3,'port':4},
                                'Hybe27':{'valve':3,'port':3},
                                'Hybe28':{'valve':3,'port':2},
                                'Vacume_A':{'valve':1,'port':2},
                                'Vacume_B':{'valve':1,'port':3},
                                'Vacume_C':{'valve':1,'port':4},
                                'Vacume_D':{'valve':1,'port':5},
                                'Vacume_E':{'valve':1,'port':6},
                                'Vacume_F':{'valve':1,'port':7},
                                'Vacume_Waste':{'valve':1,'port':10},
                                'Valve2':{'valve':3,'port':1},
                                'Valve3':{'valve':4,'port':1},
                            }