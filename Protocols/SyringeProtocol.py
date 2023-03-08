from Protocols.Protocol import *
class SyringeProtocol(Protocol):
    def __init__(self,verbose):
        self.verbose = True
        self.protocols = {}
        self.protocols['Valve'] = self.valve

    def get_steps(self,protocol,chambers,other):
        return self.protocols[protocol](chambers,other)


    def valve(self,chambers,other):
        port,volume = other.split('+')
        volume = float(volume)
        steps = []
        """ EMPTY CHAMBER """
        for chamber in chambers:
            steps.append(self.replace_volume(port,chamber,volume))
        return pd.concat(steps,ignore_index=true)

    def replace_volume(self,inport,outport,volume,speed=0,pause=0):
        steps = []
        steps.append(self.empty_chamber(outport))
        steps.append(self.add_liquid(inport,outport,volume))
        return pd.concat(steps,ignore_index=true)

    def empty_chamber(chamber,speed=0,pause=0):
        steps = []
        steps.append(self.format(port=chamber,volume=5,speed=speed,pause=pause,direction='Reverse'))
        steps.append(self.format(port='Waste',volume=5,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=true)

    def add_liquid(port,chamber,volume,speed=0,pause=0):
        steps = []
        steps.append(self.format(port=port,volume=volume,speed=speed,pause=pause,direction='Reverse'))
        steps.append(self.format(port=chamber,volume=volume,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=true)