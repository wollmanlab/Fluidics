from Protocols.Protocol import *
import pandas as pd
class SyringeProtocol(Protocol):
    def __init__(self,gui=False):
        super().__init__()
        self.verbose = True
        self.closed_volume_buffer = 0.5

    def replace_volume_single(self,inport,outport,volume,speed=0,pause=0):
        if self.vacume:
            return self.simultaneous_replace_volume_single(inport,outport,volume,speed=speed,pause=pause)
        else:
            if speed == 0:
                speed = self.speed
            steps = []
            if not ((outport=='Waste')|(inport==outport)):
                steps.append(self.empty_chamber(outport,speed=self.max_speed,pause=0))
                steps.append(self.wait(1))
            steps.append(self.add_liquid(inport,outport,volume,speed=speed,pause=pause))
            steps.append(self.wait(1))
            return pd.concat(steps,ignore_index=True)
    
    def simultaneous_replace_volume_single(self,inport,outport,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        if not ((outport=='Waste')|(inport==outport)):
            # determine Vacume Port
            vacume_chamber = 'Vacume_'+outport
            # Set Vacume To Chamber
            steps.append(self.format(port=vacume_chamber,volume=0,speed=self.speed ,pause=0,direction='Reverse'))
            steps.append(self.wait(1))
        steps.append(self.format(port=inport,volume=volume,speed=self.max_speed ,pause=0,direction='Reverse'))
        steps.append(self.wait(1))
        # Turn Off Vacume
        steps.append(self.format(port='Vacume_'+'Waste',volume=0,speed=self.speed ,pause=0,direction='Reverse'))
        steps.append(self.format(port=outport,volume=volume,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)

    def replace_volume_closed_single(self,inport,outport,volume,speed=0,pause=0,n_steps=1):
        if speed == 0:
            speed = self.speed
        steps = []
        steps.append(self.format(port=inport,volume=volume+self.closed_volume_buffer,speed=self.max_speed ,pause=0,direction='Reverse'))
        steps.append(self.wait(1))
        if n_steps==1:
            steps.append(self.format(port=outport,volume=volume,speed=speed,pause=pause,direction='Forward'))
        else:
            n_steps = int(n_steps)
            iter_volume = volume/n_steps
            iter_pause = pause/n_steps
            for s in range(n_steps):
                steps.append(self.format(port=outport,volume=iter_volume,speed=speed,pause=iter_pause,direction='Forward'))
        steps.append(self.wait(1))
        steps.append(self.format(port='Waste',volume=self.closed_volume_buffer,speed=1,pause=0,direction='Forward'))
        steps.append(self.wait(1))
        return pd.concat(steps,ignore_index=True)
    
    def add_volume_single(self,inport,outport,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        steps.append(self.empty_chamber(outport,speed=self.max_speed,pause=0))
        steps.append(self.add_liquid(inport,outport,volume,speed=speed,pause=pause))
        return pd.concat(steps,ignore_index=True)

    def empty_chamber(self,chamber,volume=5,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        if self.vacume:
            # determine Vacume Port
            vacume_chamber = 'Vacume_'+chamber
            # Set Vacume To Chamber
            steps.append(self.format(port=vacume_chamber,volume=volume,speed=self.speed ,pause=0,direction='None'))
            steps.append(self.wait(1))
        else:
            steps.append(self.format(port=chamber,volume=self.chamber_volume,speed=self.max_speed ,pause=pause,direction='Reverse'))
            steps.append(self.format(port='Waste',volume=self.chamber_volume,speed=self.max_speed ,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)

    def add_liquid(self,port,chamber,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        steps.append(self.format(port=port,volume=volume,speed=self.max_speed ,pause=0,direction='Reverse'))
        if 'hybe' in port.lower():
            steps.append(self.wait(5)) # Ensure Accurate Liquid Exchange for Hybe
        steps.append(self.format(port=chamber,volume=volume,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)