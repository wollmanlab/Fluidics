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
        self.protocols['Storage2Gel'] = self.Storage2Gel
        self.protocols['Gel2Hybe'] = self.Gel2Hybe
        self.protocols['Hybe2Image'] = self.Hybe2Image
        self.protocols['PrepSample'] = self.PrepSample

    def update_user(self,message,level=20,logger='Protocol'):
        logger = self.device +'***' + logger
        if self.verbose:
            update_user(message,level=level,logger=logger)
            
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
        time_estimate = (float(volume)/float(speed))*self.speed_conversion+1+float(pause)
        return pd.DataFrame([port,volume,speed,pause,direction,time_estimate],index = ['port','volume','speed','pause','direction','time_estimate']).T



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
        if tube == '':
            tube = 'Waste'
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
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*10))
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
    
 
    def formamide(self,chambers,port):
        steps = []
        steps.append(self.replace_volume(chambers,'FW',self.rinse_volume,speed=self.speed,pause=60*15))
        steps.append(self.replace_volume(chambers,'FW',self.rinse_volume,speed=self.speed,pause=60*15))
        steps.append(self.replace_volume(chambers,'FW',self.rinse_volume,speed=self.speed,pause=60*15))
        steps.append(self.replace_volume(chambers,'FW',self.rinse_volume,speed=self.speed,pause=60*15))
        return pd.concat(steps,ignore_index=True)
    
    def TBSTw(self,chambers,port):
        steps = []
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        return pd.concat(steps,ignore_index=True)
    
    
    def Storage2Gel(self,chambers,other):
        steps = []
        # Remove From Storage
        # for i in range(3):
        #     steps.append(self.replace_volume(chambers,'PBS',self.rinse_volume,speed=self.speed,pause=60*5))
        # # Permeabilize
        # steps.append(self.replace_volume(chambers,'TPERM',self.rinse_volume,speed=self.speed,pause=60*30))
        # # Wash
        # for i in range(3):
        #     steps.append(self.replace_volume(chambers,'PBS',self.rinse_volume,speed=self.speed,pause=60*5))
        # # Buffer Exchange
        # for i in range(3):
        #     steps.append(self.replace_volume(chambers,'MOPS',self.rinse_volume,speed=self.speed,pause=60*5))
        # # MelphaX
        # steps.append(self.replace_volume(chambers,'MelphaX',self.rinse_volume,speed=self.speed,pause=60*60*18))
        # Wash
        for i in range(3):
            steps.append(self.replace_volume(chambers,'PBS',self.rinse_volume,speed=self.speed,pause=60*5))
        # Buffer Exchange
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        return pd.concat(steps,ignore_index=True)

    def Gel2Hybe(self,chambers,other):
        steps = []
        # Wash
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        # Clearing
        for iter in range(3):
            for i in range(3):
                steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
            steps.append(self.replace_volume(chambers,'ProtKSDS',self.rinse_volume,speed=self.speed,pause=60*60*4))
        # Remove SDS
        for i in range(3):
            steps.append(self.replace_volume(chambers,'EthyleneCarbonate',self.rinse_volume,speed=self.speed,pause=60*15))
        # Wash
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        # Buffer Exchange
        for i in range(3):
            steps.append(self.replace_volume(chambers,'Formamide',self.rinse_volume,speed=self.speed,pause=60*5))
        return pd.concat(steps,ignore_index=True)


    def Hybe2Image(self,chambers,other):
        steps = []
        # Wash
        for i in range(3):
            steps.append(self.replace_volume(chambers,'Formamide',self.rinse_volume,speed=self.speed,pause=60*15))
        # Buffer Exchange
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        # Clearing
        steps.append(self.replace_volume(chambers,'ProtK',self.rinse_volume,speed=self.speed,pause=60*60*2))
        # Wash
        for i in range(3):
            steps.append(self.replace_volume(chambers,'TBS',self.rinse_volume,speed=self.speed,pause=60*5))
        return pd.concat(steps,ignore_index=True)
    
    def PrepSample(self,chambers,other):
        steps = []
        steps.append(self.Storage2Gel(chambers,other))
        steps.append(self.replace_volume(chambers,'Gel',3,speed=self.speed,pause=60*60*3))
        steps.append(self.Gel2Hybe(chambers,other))
        steps.append(self.replace_volume(chambers,'Hybe',0.5,speed=self.speed,pause=36*60*60))
        steps.append(self.Hybe2Image(chambers,other))
        return pd.concat(steps,ignore_index=True)







        