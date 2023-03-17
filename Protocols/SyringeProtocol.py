from Protocols.Protocol import *
import pandas as pd
class SyringeProtocol(Protocol):
    def __init__(self,gui=False):
        super().__init__()
        self.verbose = True

    def replace_volume_single(self,inport,outport,volume,speed=0,pause=0):
        steps = []
        steps.append(self.empty_chamber(outport,speed=speed,pause=0))
        steps.append(self.add_liquid(inport,outport,volume,speed=speed,pause=pause))
        return pd.concat(steps,ignore_index=True)
    
    def add_volume_single(self,inport,outport,volume,speed=0,pause=0):
        steps = []
        steps.append(self.empty_chamber(outport,speed=speed,pause=0))
        steps.append(self.add_liquid(inport,outport,volume,speed=speed,pause=pause))
        return pd.concat(steps,ignore_index=True)

    def empty_chamber(self,chamber,speed=0,pause=0):
        steps = []
        steps.append(self.format(port=chamber,volume=self.chamber_volume,speed=speed,pause=pause,direction='Reverse'))
        steps.append(self.format(port='Waste',volume=self.chamber_volume,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)

    def add_liquid(self,port,chamber,volume,speed=0,pause=0):
        steps = []
        steps.append(self.format(port=port,volume=volume,speed=speed,pause=0,direction='Reverse'))
        steps.append(self.format(port=chamber,volume=volume,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)