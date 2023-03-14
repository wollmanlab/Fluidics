from Protocols.Protocol import *
import pandas as pd
class SyringeProtocol(Protocol):
    def __init__(self,verbose):
        self.verbose = True
        self.protocols = {}
        self.protocols['Valve'] = self.valve
        self.protocols['Hybe'] = self.hybe
        self.protocols['Strip'] = self.strip
        self.protocols['ReverseFlush'] = self.reverse_flush
        self.protocols['Prime'] = self.prime

        self.chamber_volume = 0
        self.flush_volume = 1.5
        self.prime_volume = 1
        self.rinse_volume = 3
        self.hybe_volume = 3

        self.rinse_time = 60
        self.hybe_time = 600

    def get_steps(self,protocol,chambers,other):
        return self.protocols[protocol](chambers,other)

    def reverse_flush(self,chambers,Valve_Commands):
        steps = []
        for port in Valve_Commands.keys():
            steps.append(self.replace_volume_single(port,'TBS',self.flush_volume,speed=0,pause=0))
        return pd.concat(steps,ignore_index=True)

    def prime(self,chambers,Valve_Commands):
        steps = []
        for port in Valve_Commands.keys():
            steps.append(self.replace_volume_single('Waste',port,self.prime_volume,speed=0,pause=0))
        return pd.concat(steps,ignore_index=True)

    def hybe(self,chambers,hybe):
        steps = []
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=0,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,hybe,self.hybe_volume,speed=0,pause=self.hybe_time))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=0,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=0,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=0,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=0,pause=self.rinse_time))
        return pd.concat(steps,ignore_index=True)

    def strip(self,chambers,hybe):
        steps = []
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=0,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TCEP',self.hybe_volume,speed=0,pause=self.hybe_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=0,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=0,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=0,pause=self.rinse_time))
        return pd.concat(steps,ignore_index=True)

    def valve(self,chambers,other,):
        port,volume = other.split('+')
        volume = float(volume)
        return self.replace_volume(chambers,port,volume)

    def replace_volume(self,chambers,port,volume,speed=0,pause=0):
        steps = []
        for chamber in chambers:
            steps.append(self.replace_volume_single(port,chamber,volume,speed=speed,pause=pause))
        return pd.concat(steps,ignore_index=True)

    def replace_volume_single(self,inport,outport,volume,speed=0,pause=0):
        steps = []
        steps.append(self.empty_chamber(outport))
        steps.append(self.add_liquid(inport,outport,volume))
        return pd.concat(steps,ignore_index=True)

    def empty_chamber(self,chamber,speed=0,pause=0):
        steps = []
        steps.append(self.format(port=chamber,volume=self.chamber_volume,speed=speed,pause=pause,direction='Reverse'))
        steps.append(self.format(port='Waste',volume=self.chamber_volume,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)

    def add_liquid(self,port,chamber,volume,speed=0,pause=0):
        steps = []
        steps.append(self.format(port=port,volume=volume,speed=speed,pause=pause,direction='Reverse'))
        steps.append(self.format(port=chamber,volume=volume,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)