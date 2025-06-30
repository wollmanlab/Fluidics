import pandas as pd
import numpy as np
from fileu import *
class Protocol:
    def __init__(self,gui=False):
        self.verbose=True # When in verbose mode, update_user() will record the input message to the log.
        self.protocols = {} # A dictionary for holding all the protocols (functions).

        self.simulate = False
        self.vacume = False

        self.chamber_volume = 3 # Volume of one chamber, in the unit of mL
        self.flush_volume = 1.5 # Unknown meaning, not used anywhere
        self.prime_volume = 2 # Volume of the fluid for priming to fill all the dead volume, in the unit of mL.
        self.rinse_volume = 3 # Volume of the fluid for rinsing one chamber, in the unit of mL
        self.hybe_volume = 3 # Volume of the hybridization mixture for one chamber, in the unit of mL
        
        self.mixes = 3 # Number of mixes to do during hybridization.

        self.rinse_time = 60 # The duration for one rinse of the chamber, in the unit of sec.
        self.hybe_time = 600 # The duration for one hybridization, in the unit of sec.
        self.max_speed = 1 # The maximum speed allowed for the fluidic flow, 1 means 100% here.
        self.speed = 1 # The speed of the protocol
        self.closed_speed = 0.3 # The speed when a closed (sealed) chamber is used rather than an open chamber.
        self.wait_factor = 0
        self.speed_conversion = 1.5
        self.primed = False # Indicating whether the fluidic system has been primed or not to fill all dead volume

        # Add protocols to the dictionary.
        self.protocols['Valve'] = self.valve
        self.protocols['Clean'] = self.clean
        self.protocols['Hybe'] = self.hybe
        self.protocols['EncodingHybe'] = self.encoding_hybe
        self.protocols['FormamideStrip'] = self.formamide_strip
        self.protocols['Strip'] = self.strip
        self.protocols['ClosedValve'] = self.closed_valve
        self.protocols['ClosedStripHybeImage'] = self.closed_strip_hybe_image
        self.protocols['ClosedStripImage'] = self.closed_strip_image
        self.protocols['ClosedHybeImage'] = self.closed_hybe_image
        # self.protocols['ClosedBubbleRemover'] = self.closed_bubble_remover
        self.protocols['ReverseFlush'] = self.reverse_flush
        self.protocols['Prime'] = self.prime
        self.protocols['Storage2Gel'] = self.Storage2Gel
        self.protocols['Gel2Hybe'] = self.Gel2Hybe
        self.protocols['Hybe2Image'] = self.Hybe2Image
        self.protocols['PrepSample'] = self.PrepSample
        self.protocols['MERFISHStripVolumeCheck'] = self.MERFISHStripVolumeCheck
        self.protocols['MERFISHVolumeCheck'] = self.MERFISHVolumeCheck
        self.protocols['dredFISHVolumeCheck'] = self.dredFISHVolumeCheck
        self.protocols['dendcycle'] = self.dendcycle
        self.protocols['dendbca'] = self.dendbca
        self.protocols['blankprotocol'] = self.blankprotocol
        self.protocols['bdna'] = self.bdna
        self.protocols['dendcyclegradient'] = self.dendcyclegradient
        self.protocols['dendgradient'] = self.dendgradient

    # self.update_user() is for writing messages to the log
    def update_user(self,message,level=20,logger='Protocol'):
        logger = self.device +'***' + logger
        if self.verbose:
            update_user(message,level=level,logger=logger)
            
    # self.get_steps() executes the a protocol at user specified chambers with user specified arguments
    # protocol: the name of the protocol
    # chambers: an array specifying the chambers where the protol should be run
    # other: other arguments the protocol need besides chamber.
    def get_steps(self,protocol,chambers,other):
        steps = self.protocols[protocol](chambers,other)
        self.update_user('Executing Protocol:')
        self.update_user(steps)
        return steps
    
    def wait(self,pause):
        steps = []
        steps.append(self.format(port='',volume=0,speed=self.max_speed,pause=pause,direction='Wait'))
        return pd.concat(steps,ignore_index=True)

    def replace_volume(self,chambers,port,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        if self.vacume:
            # Empty Wells First
            for chamber in chambers:
                steps.append(self.empty_chamber(chamber,volume=volume,speed=speed,pause=0))
            steps.append(self.empty_chamber('Waste',volume=0,speed=0,pause=0))
            for chamber in chambers:
                steps.append(self.add_liquid(port,chamber,volume,speed=speed,pause=0))
        else:
            for chamber in chambers:
                steps.append(self.replace_volume_single(port,chamber,volume,speed=speed,pause=0))
        expected_time = pd.concat(steps,ignore_index=True)['time_estimate']
        expected_time =expected_time.sum()-expected_time[0:6].sum()
        pause = np.max([pause-expected_time,0])
        steps.append(self.wait(pause))
        return pd.concat(steps,ignore_index=True)
    
    def replace_volume_mix(self,chambers,port,volume,speed=0,pause=0,mixes=0):
        if speed == 0:
            speed = self.speed
        steps = []
        steps.append(self.replace_volume(chambers,port,volume,speed=speed,pause=0))
        if mixes>0:
            steps.append(self.wait(99999))
            for step in range(mixes):
                steps.append(self.mix(chambers,self.hybe_volume))
                steps.append(self.wait(99999))
            steps = pd.concat(steps,ignore_index=True)
            time_estimate = steps['time_estimate']
            pause_estimate = steps['pause']
            expected_time = np.sum(time_estimate[pause_estimate!=99999])
            total_pause_time = np.max([pause-expected_time,0])
            time_estimate[pause_estimate==99999] = 1+total_pause_time/(mixes+1)
            pause_estimate[pause_estimate==99999] = total_pause_time/(mixes+1)
            steps['time_estimate'] = time_estimate
            steps['pause'] = pause_estimate
            return steps
        else:
            steps.append(self.wait(pause))
            return pd.concat(steps,ignore_index=True)
    
    def add_volume(self,chambers,port,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        for chamber in chambers:
            steps.append(self.add_liquid(port,chamber,volume,speed=speed,pause=0))
        expected_time = pd.concat(steps,ignore_index=True)['time_estimate'].sum()
        pause = np.max([pause-expected_time,0])
        steps.append(self.wait(pause))
        return pd.concat(steps,ignore_index=True)

    def replace_volume_closed(self,chambers,port,volume,speed=0,pause=0,n_steps=1):
        if speed == 0:
            speed = self.speed
        steps = []
        if len(chambers)==1:
            steps.append(self.replace_volume_closed_single(port,chambers[0],volume,speed=speed,pause=pause,n_steps=n_steps))
        else:
            for chamber in chambers:
                steps.append(self.replace_volume_closed_single(port,chamber,volume,speed=speed,pause=0,n_steps=n_steps))
            steps.append(self.wait(pause))
        return pd.concat(steps,ignore_index=True)

    def format(self,port='A',volume=0,speed=1,pause=0,direction='Forward'):
        time_estimate = ((float(volume)/float(speed))*self.speed_conversion)+1+float(pause)
        return pd.DataFrame([port,volume,speed,pause,direction,time_estimate],index = ['port','volume','speed','pause','direction','time_estimate']).T

    def mix(self,chambers,volume):
        steps = []
        for chamber in chambers:
            steps.append(self.replace_volume_single(chamber,chamber,volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)
    
    def valve(self,chambers,other):
        port,volume = other.split('+')
        volume = float(volume)
        return self.replace_volume(chambers,port,volume)

    def closed_valve(self,chambers,other):
        port,volume = other.split('+')
        volume = float(volume)
        return self.replace_volume_closed(chambers,port,volume,speed=self.closed_speed)

    """ PUT YOUR PROTOCOLS BELOW HERE"""
    def mineral(self,volume):
        # if '+' in tube:
        #     tube,volume  =tube.split('+')
        #     volume = float(volume)
        steps = []
        steps.append(self.format(port='MOil',volume=self.rinse_volume/2,speed=self.closed_speed*2,pause=10,direction='Reverse'))
        steps.append(self.format(port='IBuffer',volume=self.rinse_volume/2,speed=self.max_speed,pause=0,direction='Forward'))
        steps.append(self.format(port='IBuffer',volume=volume+self.rinse_volume+self.closed_volume_buffer,speed=self.closed_speed,pause=30,direction='Reverse'))
        steps.append(self.format(port='M',volume=self.rinse_volume,speed=self.closed_speed,pause=0,direction='Forward'))
        steps.append(self.format(port='Air',volume=self.rinse_volume,speed=self.max_speed,pause=0,direction='Reverse'))
        steps.append(self.format(port='Waste',volume=volume+self.rinse_volume+self.closed_volume_buffer,speed=self.max_speed,pause=5,direction='Forward'))
        n = 3
        for i in range(n):
            steps.append(self.format(port='TBS',volume=self.rinse_volume,speed=self.max_speed,pause=5,direction='Reverse'))
            steps.append(self.format(port='Waste',volume=self.rinse_volume,speed=self.max_speed,pause=5,direction='Forward'))
        return pd.concat(steps,ignore_index=True) 
    

    def reverse_flush(self,Valve_Commands,tube):
        tube,volume = tube.split('+')
        volume = float(volume)
        steps = []
        for port in Valve_Commands.keys():
            if ('Vacume' in port)|('Air' in port):
                continue
            steps.append(self.add_liquid(tube,port,float(volume),speed=self.max_speed,pause=0))
        return pd.concat(steps,ignore_index=True)
    
    def clean(self,Valve_Commands,tube):
        steps = []
        if not '+' in tube:
            tube = tube+'+5'
        old_max_speed = self.max_speed
        self.max_speed = 1
        steps.append(self.reverse_flush(Valve_Commands,tube))
        steps.append(self.prime(Valve_Commands,tube))
        steps.append(self.reverse_flush(Valve_Commands,'Air+3'))
        steps.append(self.reverse_flush(Valve_Commands,'Air+3'))
        self.max_speed = old_max_speed
        return pd.concat(steps,ignore_index=True)

    def prime(self,Valve_Commands,tube):
        tube,volume = tube.split('+')
        if tube == '':
            tube = 'Waste'
        volume = float(volume)
        steps = []
        for port in Valve_Commands.keys():
            if ('Vacume' in port)|('Air' in port):
                continue
            steps.append(self.add_liquid(port,tube,volume,speed=self.max_speed,pause=0))
        return pd.concat(steps,ignore_index=True)

    def dendcycle(self,chambers,hybe):
        wait_time = 60*60 #always 30 min hybes
        if '+' in hybe:
            hybe,wait_time = hybe.split('+')
            wait_time = 60*int(wait_time) # minutes
        if not 'Hybe' in hybe:
            hybe = 'Hybe'+str(hybe)
        steps = []

        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,hybe,self.hybe_volume,speed=self.speed,pause=wait_time))

        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=0))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)
    
    def dendcyclegradient(self,chambers,hybe):
        wait_time = 60*60 #always 30 min hybes
        if '+' in hybe:
            hybe,wait_time = hybe.split('+')
            wait_time = 60*int(wait_time) # minutes
        steps = []

        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))

        steps.append(self.replace_volume('A', str('Hybe' + str(1*int(hybe)+0)),self.hybe_volume,speed=self.speed,pause=0))
        steps.append(self.replace_volume('B',str('Hybe' + str(1*int(hybe)+3)),self.hybe_volume,speed=self.speed,pause=0))
        steps.append(self.replace_volume('C',str('Hybe' + str(1*int(hybe)+6)),self.hybe_volume,speed=self.speed,pause=0))
        steps.append(self.replace_volume("D",str('Hybe' + str(1*int(hybe)+9)),self.hybe_volume,speed=self.speed,pause=0))
        steps.append(self.replace_volume('E',str('Hybe' + str(1*int(hybe)+12)),self.hybe_volume,speed=self.speed,pause=0))
        steps.append(self.replace_volume('F',str('Hybe' + str(1*int(hybe)+15)),self.hybe_volume,speed=self.speed,pause=wait_time))

        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=0))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)
    
    def blankprotocol(self,chambers,hybe):
        steps = []
        #steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        return steps


    def dendbca(self,chambers,hybe):
        steps = []
        b = self.dendcycle(chambers, 'Hybe2')
        c = self.dendcycle(chambers, 'Hybe3')
        a = self.dendcycle(chambers, 'Hybe1')

        steps.append(b)
        steps.append(c)
        steps.append(a)

        return pd.concat(steps,ignore_index = True)
    
    def dendgradient(self,chambers,hybe):
        steps = []
        b = self.dendcyclegradient(chambers, '2')
        c = self.dendcyclegradient(chambers, '3')
        a = self.dendcyclegradient(chambers, '1')

        steps.append(a)
        steps.append(b)
        steps.append(c)

        return pd.concat(steps,ignore_index = True)

    def bdna(self,chambers,hybe):
        wait_time = 60*60
        if '+' in hybe:
            hybe,wait_time = hybe.split('+')
            wait_time = 60*int(wait_time) # minutes
        hybe = 'Hybe26'
        steps = []

        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','WBuffer':''},'Waste+'+str(self.prime_volume)))
            if not self.simulate:
                self.primed = True
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.prime({hybe:''},'Waste+'+str(self.prime_volume)))
        steps.append(self.replace_volume_mix(chambers,hybe,self.hybe_volume,speed=self.speed,pause=wait_time,mixes=3))
        steps.append(self.add_liquid('Air',hybe,float(3),speed=self.speed,pause=0)) # Reset Tube to resting state
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time*2.5))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time*2.5))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=0))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)
    
    def hybe(self,chambers,hybe):
        wait_time = self.hybe_time
        WBuffer = 'WBuffer'
        if '+' in hybe:
            hybe,wait_time = hybe.split('+')
            if '&' in wait_time:
                wait_time,WBuffer = wait_time.split('&')
            wait_time = 60*int(wait_time) # minutes
        if not 'Hybe' in hybe:
            hybe = 'Hybe'+str(hybe)
        steps = []
        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','HybeTBS':'','StripTBS':'',WBuffer:''},'Waste+'+str(self.prime_volume)))
            if not self.simulate:
                self.primed = True
        steps.append(self.replace_volume(chambers,WBuffer,self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.prime({hybe:''},'Waste+'+str(self.prime_volume)))
        steps.append(self.replace_volume_mix(chambers,hybe,self.hybe_volume,speed=self.speed,pause=wait_time,mixes=self.mixes))
        steps.append(self.add_liquid('Air',hybe,float(3),speed=self.speed,pause=0)) # Reset Tube to resting state
        steps.append(self.replace_volume(chambers,WBuffer,self.rinse_volume,speed=self.speed,pause=self.rinse_time*2.5))
        steps.append(self.replace_volume(chambers,WBuffer,self.rinse_volume,speed=self.speed,pause=self.rinse_time*2.5))
        steps.append(self.replace_volume(chambers,'HybeTBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'HybeTBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'HybeTBS',self.rinse_volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)
    
    def encoding_hybe(self,chambers,hybe):
        wait_time = self.hybe_time * 3
        if '+' in hybe:
            hybe,wait_time = hybe.split('+')
            wait_time = 60*int(wait_time) # minutes
        if not 'Hybe' in hybe:
            hybe = 'Hybe'+str(hybe)
        steps = []
        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','HybeTBS':'','StripTBS':'','WBuffer':''},'Waste+'+str(self.prime_volume)))
            if not self.simulate:
                self.primed = True
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.prime({hybe:''},'Waste+'+str(self.prime_volume)))
        steps.append(self.replace_volume_mix(chambers,hybe,self.hybe_volume,speed=self.speed,pause=wait_time,mixes=3))
        steps.append(self.add_liquid('Air',hybe,float(3),speed=self.speed,pause=0)) # Reset Tube to resting state
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time*5))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time*5))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time*5))
        steps.append(self.replace_volume(chambers,'HybeTBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'HybeTBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'HybeTBS',self.rinse_volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)

    def strip(self,chambers,port,n=3):
        wait_time = self.hybe_time
        if '+' in port:
            port,wait_time = port.split('+')
            if '&' in wait_time:
                wait_time = wait_time.split('&')[0]
            wait_time = 60*int(wait_time) # minutes
        steps = []
        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','HybeTBS':'','StripTBS':'','WBuffer':''},'Waste+'+str(self.prime_volume)))
            if not self.simulate:
                self.primed = True
        for i in range(n):
            steps.append(self.replace_volume_mix(chambers,'TCEP',self.hybe_volume,speed=self.speed,pause=wait_time/n,mixes=self.mixes))
        steps.append(self.replace_volume(chambers,'StripTBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time*2.5))
        steps.append(self.replace_volume(chambers,'StripTBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time*2.5))
        steps.append(self.replace_volume(chambers,'StripTBS',self.rinse_volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)
    
    def formamide_strip(self,chambers,port):
        wait_time = self.hybe_time
        if '+' in port:
            port,wait_time = port.split('+')
            wait_time = 60*int(wait_time) # minutes
        steps = []
        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','WBuffer':''},'Waste+'+str(self.prime_volume)))
            if not self.simulate:
                self.primed = True
        n = 3
        for i in range(n):
            steps.append(self.replace_volume_mix(chambers,'TCEP',self.hybe_volume,speed=self.speed,pause=wait_time/n,mixes=3))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time*2.5))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time*2.5))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)
    
    
    def closed_bubble_remover(self,chambers,tube):
        tube  =tube.split('+')[0]
        steps = []
        for chamber in chambers:
            steps.append(self.replace_volume_closed_single(tube,chamber,self.rinse_volume,speed=self.closed_speed,pause=0,n_steps=1))
            steps.append(self.replace_volume_closed_single(tube,chamber,self.rinse_volume,speed=self.closed_speed,pause=0,n_steps=1))
            steps.append(self.replace_volume_closed_single(tube,chamber,self.rinse_volume,speed=self.closed_speed,pause=0,n_steps=1))
            steps.append(self.replace_volume_closed_single(tube,chamber,self.rinse_volume,speed=self.closed_speed,pause=0,n_steps=1))
            backup_max_speed = self.max_speed
            self.max_speed = self.closed_speed
            steps.append(self.replace_volume_closed_single(chamber,'Waste',1,speed=backup_max_speed,pause=0,n_steps=1))
            self.max_speed = backup_max_speed
        return pd.concat(steps,ignore_index=True)


    def closed_strip_image(self,chambers,hybe):
        if not 'Hybe' in hybe:
            hybe = 'Hybe'+hybe
        steps = []
        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','WBuffer':'','IBuffer':''},'Waste+2'))
            if not self.simulate:
                self.primed = True
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TCEP',self.hybe_volume,speed=self.closed_speed,pause=self.hybe_time,n_steps=3))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'IBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.format(port='Waste',volume=0.45,speed=1,pause=0,direction='Forward'))
        # steps.append(self.mineral(volume=1))
        return pd.concat(steps,ignore_index=True)

    def closed_strip_hybe_image(self,chambers,hybe):
        if not 'Hybe' in hybe:
            hybe = 'Hybe'+hybe
        steps = []
        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','WBuffer':'','IBuffer':''},'Waste+2'))
            if not self.simulate:
                self.primed = True
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TCEP',self.hybe_volume,speed=self.closed_speed,pause=self.hybe_time,n_steps=3))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.prime({hybe:''},'Waste+2'))
        steps.append(self.replace_volume_closed(chambers,hybe,self.hybe_volume,speed=self.closed_speed,pause=self.hybe_time*2,n_steps=3))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'IBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.format(port='Waste',volume=0.45,speed=1,pause=0,direction='Forward'))
        # steps.append(self.mineral(volume=1))
        return pd.concat(steps,ignore_index=True)
    
    def closed_hybe_image(self,chambers,hybe):
        if not 'Hybe' in hybe:
            hybe = 'Hybe'+hybe
        steps = []
        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','WBuffer':'','IBuffer':''},'Waste+2'))
            if not self.simulate:
                self.primed = True
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.prime({hybe:''},'Waste+2'))
        steps.append(self.replace_volume_closed(chambers,hybe,self.hybe_volume,speed=self.closed_speed,pause=self.hybe_time*2,n_steps=3))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'IBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.format(port='Waste',volume=0.45,speed=1,pause=60*4,direction='Forward'))
        # steps.append(self.mineral(volume=1))
        return pd.concat(steps,ignore_index=True)
    
    # def closed_hybe_image(self,chambers,hybe):
    #     if not 'Hybe' in hybe:
    #         hybe = 'Hybe'+hybe
    #     steps = []
    #     if not self.primed:
    #         steps.append(self.prime({'TCEP':'','TBS':'','WBuffer':'','IBuffer':''},'Waste+2'))
    #         if not self.simulate:
    #             self.primed = True
    #     # steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     # steps.append(self.replace_volume_closed(chambers,'TCEP',self.hybe_volume,speed=self.closed_speed,pause=self.hybe_time,n_steps=3))
    #     # steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     steps.append(self.prime({hybe:''},'Waste+2'))
    #     steps.append(self.replace_volume_closed(chambers,hybe,self.hybe_volume,speed=self.closed_speed,pause=self.hybe_time,n_steps=3))
    #     steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     steps.append(self.replace_volume_closed(chambers,'IBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
    #     return pd.concat(steps,ignore_index=True)
    
    def Storage2Gel(self,chambers,other):
        steps = []
        # Remove From Storage
        for i in range(2):
            steps.append(self.replace_volume(chambers,'PBS',self.rinse_volume,speed=self.speed,pause=60*10))
        # Permeabilize
        steps.append(self.replace_volume(chambers,'TPERM',self.rinse_volume,speed=self.speed,pause=60*30))
        # Wash
        for i in range(2):
            steps.append(self.replace_volume(chambers,'MOPS',self.rinse_volume,speed=self.speed,pause=60*10))
        # MelphaX
        steps.append(self.replace_volume(chambers,'MelphaX',self.hybe_volume,speed=self.speed,pause=60*60*1))

        # steps.append(self.add_volume(chambers,'Air',self.hybe_volume,speed=self.speed,pause=60*60*1))
        # Wash
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        # Gel
        steps.append(self.replace_volume(chambers,'Gel',self.rinse_volume,speed=self.speed,pause=0))
        return pd.concat(steps,ignore_index=True)

    def Gel2Hybe(self,chambers,other):
        wait_time = 6
        if '+' in other:
            wait_time = int(other.split('+')[-1]) # hours
        steps = []
        # Wash
        for i in range(1):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
        # Clearing
        for iter in range(1):
            steps.append(self.replace_volume(chambers,'ProtK',self.rinse_volume,speed=self.speed,pause=60*60*wait_time))
        # Wash
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        # Buffer Exchange
        for i in range(1):
            steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=60*10))
        return pd.concat(steps,ignore_index=True)


    def Hybe2Image(self,chambers,other):
        steps = []
        if '+' in other:
            wait_time = 60*60*int(other.split('+')[-1]) # hours
            steps.append(self.wait(wait_time)) 
        # Wash
        for i in range(4):
            steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=60*15))
        # Buffer Exchange
        for i in range(1):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
        # Clearing
        steps.append(self.replace_volume(chambers,'ProtK',self.rinse_volume,speed=self.speed,pause=60*60*2))
        #Wash
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
        return pd.concat(steps,ignore_index=True)
    
    
    def PrepSample(self,chambers,other):
        steps = []
        steps.append(self.Storage2Gel(chambers,other))
        # steps.append(self.replace_volume(chambers,'Gel',3,speed=self.speed,pause=60*60*3))
        steps.append(self.Gel2Hybe(chambers,other))
        # steps.append(self.replace_volume(chambers,'Hybe',0.5,speed=self.speed,pause=36*60*60))
        steps.append(self.Hybe2Image(chambers,other))
        return pd.concat(steps,ignore_index=True)
    
    def MERFISHStripVolumeCheck(self,chambers,other):
        primed = self.primed
        self.primed = True
        n_hybes = 19
        if '+' in other:
            other,n_hybes = other.split('+')
            n_hybes = int(n_hybes)
        steps = []
        for i in range(n_hybes):
            steps.append(self.closed_strip_image(chambers,str(i)))
            steps.append(self.closed_hybe_image(chambers,str(i)))
        self.primed = primed
        return pd.concat(steps,ignore_index=True)
    
    def MERFISHVolumeCheck(self,chambers,other):
        primed = self.primed
        self.primed = True
        n_hybes = 19
        if '+' in other:
            other,n_hybes = other.split('+')
            n_hybes = int(n_hybes)
        steps = []
        for i in range(n_hybes):
            steps.append(self.closed_strip_hybe_image(chambers,str(i)))
        self.primed = primed
        return pd.concat(steps,ignore_index=True)
    
    def dredFISHVolumeCheck(self,chambers,other):
        primed = self.primed
        self.primed = True
        n_hybes = 25
        if '+' in other:
            other,n_hybes = other.split('+')
            n_hybes = int(n_hybes)
        steps = []
        for i in range(n_hybes):
            steps.append(self.strip(chambers,str(i)))
            steps.append(self.hybe(chambers,str(i)))
        self.primed = primed
        return pd.concat(steps,ignore_index=True)




        
