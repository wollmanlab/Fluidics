import pandas as pd
from fileu import *
class Protocol:
    def __init__(self,gui=False):
        self.verbose=True
        self.protocols = {}



        self.chamber_volume = 5
        self.flush_volume = 1.5
        self.prime_volume = 1
        self.rinse_volume = 3
        self.hybe_volume = 3

        self.rinse_time = 60
        self.hybe_time = 600
        self.max_speed = 1
        self.speed = 1
        self.closed_speed = 1#0.25
        self.wait_factor = 0
        self.speed_conversion = 1.5
        self.primed = False

        self.protocols['Valve'] = self.valve
        self.protocols['Hybe'] = self.hybe
        self.protocols['Strip'] = self.strip
        self.protocols['ReverseFlush'] = self.reverse_flush
        self.protocols['Prime'] = self.prime
        self.protocols['Clear'] = self.clear
        self.protocols['ClosedStripHybeImage'] = self.closed_strip_hybe_image
        self.protocols['ClosedValve'] = self.closed_valve
        self.protocols['ClearAB'] = self.clear_AB
        self.protocols['ClosedBubbleRemover'] = self.closed_bubble_remover

    def update_user(self,message,level=20):
        if self.verbose:
            update_user(message,level=level,logger=None)
            
    def get_steps(self,protocol,chambers,other):
        steps = self.protocols[protocol](chambers,other)
        self.update_user('Executing Protocol:')
        self.update_user(steps)
        return steps
    
    def wait(self,pause):
        steps = []
        steps.append(self.format(port='',volume=0,speed=1,pause=pause,direction='Wait'))
        return pd.concat(steps,ignore_index=True)

    def replace_volume(self,chambers,port,volume,speed=0,pause=0):
        if speed == 0:
            speed = self.speed
        steps = []
        for chamber in chambers:
            steps.append(self.replace_volume_single(port,chamber,volume,speed=speed,pause=0))
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
        return pd.DataFrame([port,volume,speed,pause,direction],index = ['port','volume','speed','pause','direction']).T



    """ PUT YOUR PROTOCOLS BELOW HERE"""


    def reverse_flush(self,Valve_Commands,tube):
        tube,volume = tube.split('+')
        volume = float(volume)
        steps = []
        for port in Valve_Commands.keys():
            steps.append(self.add_liquid(tube,port,float(volume),speed=1,pause=0))
        return pd.concat(steps,ignore_index=True)

    def prime(self,Valve_Commands,tube):
        tube,volume = tube.split('+')
        volume = float(volume)
        steps = []
        for port in Valve_Commands.keys():
            steps.append(self.add_liquid(port,tube,volume,speed=1,pause=0))
        return pd.concat(steps,ignore_index=True)

    def hybe(self,chambers,hybe):
        hybe = 'Hybe'+str(hybe)
        steps = []
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,hybe,self.hybe_volume,speed=self.speed,pause=self.hybe_time))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'WBuffer',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        return pd.concat(steps,ignore_index=True)

    def strip(self,chambers,port):
        steps = []
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TCEP',self.hybe_volume,speed=self.speed,pause=self.hybe_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=self.rinse_time))
        return pd.concat(steps,ignore_index=True)
    
    def clear(self,chambers,iterations):
        iterations = int(iterations.split('+')[-1])
        steps = []
        for iter in range(iterations):
            for i in range(3):
                steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
            steps.append(self.replace_volume(chambers,'ProtK',self.rinse_volume,speed=self.speed,pause=60*60*4))
        return pd.concat(steps,ignore_index=True)
    
    def clear_AB(self,chambers,iterations):
        chambers = ['A','B']
        iterations = int(iterations.split('+')[-1])
        steps = []
        for iter in range(iterations):
            for i in range(3):
                steps.append(self.replace_volume(chambers,'TBS',3,speed=self.speed,pause=60*5))
            steps.append(self.replace_volume_single('ProtKSDS','A',3,speed=self.speed,pause=0))
            steps.append(self.replace_volume_single('ProtK','B',3,speed=self.speed,pause=0))
            steps.append(self.wait(60*60*4))
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',3,speed=self.speed,pause=60*5))
        return pd.concat(steps,ignore_index=True)

    def valve(self,chambers,other):
        port,volume = other.split('+')
        volume = float(volume)
        return self.replace_volume(chambers,port,volume)

    def closed_valve(self,chambers,other):
        port,volume = other.split('+')
        volume = float(volume)
        return self.replace_volume_closed(chambers,port,volume,speed=self.closed_speed)
    
    def closed_bubble_remover(self,chambers,tube):
        steps = []
        for chamber in chambers:
            steps.append(self.replace_volume_closed_single(tube,chamber,self.rinse_volume,speed=self.closed_speed,pause=0,n_steps=1))
            steps.append(self.replace_volume_closed_single(tube,chamber,self.rinse_volume,speed=self.closed_speed,pause=0,n_steps=1))
            steps.append(self.replace_volume_closed_single(tube,chamber,self.rinse_volume,speed=self.closed_speed,pause=0,n_steps=1))
            backup_max_speed = self.max_speed
            self.max_speed = self.closed_speed
            steps.append(self.replace_volume_closed_single(chamber,'Waste',self.rinse_volume,speed=backup_max_speed,pause=0,n_steps=1))
            self.max_speed = backup_max_speed
        return pd.concat(steps,ignore_index=True)


    def closed_strip_hybe_image(self,chambers,hybe):
        if not 'Hybe' in hybe:
            hybe = 'Hybe'+hybe
        steps = []
        if not self.primed:
            steps.append(self.prime({'TCEP':'','TBS':'','WBuffer':'','IBuffer':''},'Waste+2'))
            self.primed = True
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TCEP',self.hybe_volume,speed=self.closed_speed,pause=self.hybe_time,n_steps=3))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.prime({hybe:''},'Waste+2'))
        steps.append(self.replace_volume_closed(chambers,hybe,self.hybe_volume,speed=self.closed_speed,pause=self.hybe_time,n_steps=3))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'WBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'TBS',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        steps.append(self.replace_volume_closed(chambers,'IBuffer',self.rinse_volume,speed=self.closed_speed,pause=self.rinse_time))
        return pd.concat(steps,ignore_index=True)
    
    