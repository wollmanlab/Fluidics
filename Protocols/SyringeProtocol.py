from Protocols.Protocol import *
import pandas as pd
class SyringeProtocol(Protocol):
    """
    Definition of the subclass SyringeProtocol.
    For all the methods defined below,
    inport is the port where you draw solution from;
    outport is the port where you inject solution into.
    In short, you move solution from inport to outport.
    Please refer to the README of the Protocol Class for meaning of port, chamber, volume, speed and pause.
    """
    def __init__(self,gui=False):
        super().__init__()
        self.verbose = True # When in verbose mode, update_user() will record the input message to the log.
        self.closed_volume_buffer = 0.5 # Volume of closed chamber in the unit of mL. Matters only when you are using a closed chamber.

    # replace_volume_single():
    # A wrapper function for replacing solution in a single chamber.
    # If vacuum is available, it calls self.simultaneous_replace_volume_single(). 
    # When vacuum is not available, it calls empty_chamber()-> wait for 1 sec -> calls add_liquid() -> wait for 1 sec.
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

    # simultaneous_replace_volume_single(): 
    # Simultaneously empty the chamber through vacuum and draw solution from inport, then turn off vacuum and inject to outport
    # When outport=='Waste', it will draw solution from inport and inject it into the waste container. Chamber will NOT be emptied.
    # When inport==outport, it will draw solution from inport and then pump it back, can be used for mixing. Chamber will NOT be emptied
    def simultaneous_replace_volume_single(self,inport,outport,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        # Skip emptying the chamber when outport~=='Waste' or inport=~==outport
        if not ((outport=='Waste')|(inport==outport)):
            # Get the port name for vacuum aspiration of the chamber.
            vacume_chamber = 'Vacume_'+outport
            # Begin vacuum aspiration by switching to the vacuum port.
            steps.append(self.format(port=vacume_chamber,volume=0,speed=self.speed ,pause=0,direction='Reverse'))
            steps.append(self.wait(1))
        # Load solution to be injected from inport
        steps.append(self.format(port=inport,volume=volume,speed=self.max_speed ,pause=0,direction='Reverse'))
        steps.append(self.wait(1))
        # Stop vacuum aspiration. 'Vacume_Waste' is a port that blocks vacuum.
        steps.append(self.format(port='Vacume_'+'Waste',volume=0,speed=self.speed ,pause=0,direction='Reverse'))
        # Inject loaded solution into the chamber through outport
        steps.append(self.format(port=outport,volume=volume,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)

    # replace_volume_closed_single():
    # Replacing solution in a closed chamber by injecting new solution into it.
    # n_steps: Break the injection into n_steps with (pause/n_steps)sec of interval in between to avoid rapid buildup of pressure. 
    def replace_volume_closed_single(self,inport,outport,volume,speed=0,pause=0,n_steps=1):
        if speed == 0:
            speed = self.speed
        steps = []
        # To ensure correct volume of solution can be injected, an extra closed_volume_buffer amount of buffer is loaded
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
        # Pump remaining solution to waste container
        steps.append(self.format(port='Waste',volume=self.closed_volume_buffer,speed=1,pause=0,direction='Forward'))
        steps.append(self.wait(1))
        return pd.concat(steps,ignore_index=True)

    # add_volume_single():
    # It first empties a chamber and then add solution to it.
    def add_volume_single(self,inport,outport,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        steps.append(self.empty_chamber(outport,speed=self.max_speed,pause=0))
        steps.append(self.add_liquid(inport,outport,volume,speed=speed,pause=pause))
        return pd.concat(steps,ignore_index=True)

    # empty_chamber():
    # Use vacuum (if available) or syringe pump to empty a chamber
    # volume only matters when using syringe pump to empty a chamber
    def empty_chamber(self,chamber,volume=5,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        if self.vacume:
            # Get the port name for vacuum aspiration of the chamber.
            vacume_chamber = 'Vacume_'+chamber
            if chamber=='Waste':
                # Switches to 'Vacume_Waste' which is a port for just blocking the vacuum.
                steps.append(self.format(port=vacume_chamber,volume=0,speed=self.speed ,pause=0,direction='None'))
            else:
                dual_vacume=True
                if dual_vacume:
                    # When dual_vacume is ture, both syringe and vacuum is used to remove solution from the chamber.
                    # Turn on vacuum
                    steps.append(self.format(port=vacume_chamber,volume=0,speed=self.speed ,pause=0,direction='None'))
                    temp_max_speed = self.max_speed
                    self.max_speed = 1
                    # Use Syringe pump to further speed up the removal of solution
                    steps.append(self.format(port=chamber,volume=self.chamber_volume,speed=self.max_speed ,pause=pause,direction='Reverse'))
                    steps.append(self.format(port='Waste',volume=self.chamber_volume,speed=self.max_speed ,pause=pause,direction='Forward'))
                    self.max_speed = temp_max_speed
                else:
                    # When dual_vacume is false, only vacuum is used for removing solution
                    steps.append(self.format(port=vacume_chamber,volume=volume,speed=self.speed ,pause=0,direction='None'))
                    steps.append(self.wait(1))
        else:
            # Use syringe pump to remove solution from chamber and inject it into Waste.
            steps.append(self.format(port=chamber,volume=self.chamber_volume,speed=self.max_speed ,pause=pause,direction='Reverse'))
            steps.append(self.format(port='Waste',volume=self.chamber_volume,speed=self.max_speed ,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)

    # add_liquid():
    # Get solution from port and inject it to chamber. 
    def add_liquid(self,port,chamber,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        # Load solution from port
        steps.append(self.format(port=port,volume=volume,speed=self.max_speed ,pause=0,direction='Reverse'))
        # steps.append(self.format(port='Air',volume=1,speed=self.max_speed ,pause=0,direction='Reverse'))
        
        # If the port is for hybe (readout probe), wait for extra 5 sec to ensure accurate volume of 
        # readout probe is loaded
        if 'hybe' in port.lower():
            steps.append(self.wait(5))

        # Inject solution into the chamber.
        steps.append(self.format(port=chamber,volume=volume,speed=speed,pause=pause,direction='Forward'))
        # steps.append(self.format(port=chamber,volume=1,speed=speed,pause=pause,direction='Forward'))
        return pd.concat(steps,ignore_index=True)
