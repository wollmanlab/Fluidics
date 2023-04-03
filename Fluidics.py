import serial
import time
import pandas as pd
import numpy as np
from fileu import *
from Pumps.Pump import Pump as Pump
from Protocols.Protocol import Protocol as Protocol
from Valves.ViciValve import Valve as Valve
import argparse
import importlib
import threading
import sys
import os
from math import floor,ceil

dir = os.path.dirname(os.path.abspath(__file__))
for file in os.listdir(dir):
    if os.path.isdir(os.path.join(dir,file)):
        sys.path.append(os.path.join(dir,file))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fluidics_class", type=str, dest="fluidics_class", default="Fluidics", action='store', help="Which Fluidics Class to use")
    args = parser.parse_args()



class Fluidics(object):
    def __init__(self,gui=False):
        self.verbose=True
        # self.Protocol = Protocol(gui=gui)
        # self.Pump = Pump(gui=gui)
        # self.Valve = Valve(gui=gui)
        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'Status.txt')
        print(self.file_path)
        self.last_message = ""
        self.Valve_Commands = {}
        self.busy=False

        # self.thread = threading.Thread(target=self.run)
        # self.thread.daemon = True # without the daemon parameter, the function in parallel will continue even your main program ends
        # self.thread.start()
        if not gui:
            self.update_communication('Available')

    def update_user(self,message,level=20,logger='Fluidics'):
        if self.verbose:
            update_user(message,level=level,logger=logger)

    def run(self):
        if not self.busy:
            # Read Communication
            current_message = self.read_communication()
            if self.last_message!=current_message:
                self.last_message = current_message
                print(current_message)
            if 'Command' in current_message:
                print(current_message)
                self.busy = True
                # interpret message
                message = current_message.split(':')[-1]
                self.update_communication('Running:'+message)
                protocol,chambers,other = self.interpret_message(message)
                self.execute_protocol(protocol,chambers,other)
                self.update_communication('Finished:'+message)
                self.busy = False
        precise_sleep(5)

    def read_communication(self):
        with open(self.file_path,'r') as f:
            message = f.read()
        if self.last_message !=message:
            self.last_message = message
            self.update_user(message)
        return message

    def update_communication(self,message):
        self.update_user(message)
        with open(self.file_path,'w') as f:
                f.write(message)

    def interpret_message(self,message):
        protocol,chambers,other = message.split('*')
        if '!' in other:
            other = other.split('!')[0]
            self.simulate = True
        chambers = chambers[1:-1].split(',')
        if 'Flush' in protocol:
            chambers = self.Valve_Commands
        if 'Prime' in protocol:
            chambers = self.Valve_Commands
        return protocol,chambers,other

    def execute_protocol(self,protocol,chambers,other):
        steps = self.Protocol.get_steps(protocol,chambers,other)
        if not isinstance(steps,pd.DataFrame):
            self.update_user('Unknown Protocol: '+str(protocol))
        else:
            self.summarize_protocol(steps)
            if not self.simulate:
                for idx,step in steps.iterrows():
                    self.update_user(pd.DataFrame(step).T)
                    if step.direction == 'Wait':
                        precise_sleep(step.pause)
                    else:
                        self.flow(step.port,step.volume,step.speed,step.pause,step.direction)
            else:
                precise_sleep(60*0.5) # wait 0.5 minutes
        self.simulate = False

    def flow(self,port,volume,speed,pause,direction):
        self.set_port(port)
        self.start_flow(volume,direction,speed)
        self.sleep(pause)

    def set_port(self,command):
        if not command in self.Valve_Commands.keys():
            self.update_user('          Unknown Tube: '+command)
        else:
            # self.update_user('          Tube: '+command)
            """ Set Port """
            self.Valve.set_port(int(self.Valve_Commands[command]['valve'])-1, int(self.Valve_Commands[command]['port'])-1)
            command = 'Valve'+str(self.Valve_Commands[command]['valve'])
            while command in self.Valve_Commands.keys():
                self.Valve.set_port(int(self.Valve_Commands[command]['valve'])-1, int(self.Valve_Commands[command]['port'])-1)
                command = 'Valve'+str(self.Valve_Commands[command]['valve'])

    def start_flow(self,volume,direction,speed):
        if volume>0:
            self.Pump.start_flow(volume,direction,speed)

    def sleep(self,t):
        if t>0:
            self.update_user('          Wait '+str(round(t))+'s')
            for i in range(10):
                time.sleep(t/10)
                if t>0:
                    self.update_user('          '+str(round((i+1)*10))+'% Complete')

    def summarize_protocol(self,steps):
        self.update_user('Protocol Summary')
        ports = np.unique(steps['port'])
        for port in ports:
            if len(port)>1:
                total_volume = np.sum([float(i) for i in steps[(steps['port']==port)&(steps['direction']=='Reverse')]['volume']])
                if total_volume>0:
                    self.update_user('Port: '+str(port)+'  Total Volume: '+str(total_volume)+'mL')
        total_time= np.sum([float(i) for i in steps['time_estimate'] if i!=''])
        if total_time<60:
            self.update_user('Estimated Total Time: '+str(int(total_time))+'s')
        elif total_time<60*60:
            minutes = floor(total_time/60)
            total_time = total_time-(minutes*60)
            self.update_user('Estimated Total Time: '+str(int(minutes))+'m'+str(int(total_time))+'s')
        else:
            hours = floor(total_time/(60*60))
            total_time = total_time-(hours*60*60)
            minutes = floor(total_time/60)
            total_time = total_time-(minutes*60)
            self.update_user('Estimated Total Time: '+str(int(hours))+'h'+str(int(minutes))+'m'+str(int(total_time))+'s')

if __name__ == '__main__':
    fluidics_class = args.fluidics_class
    module = importlib.import_module(fluidics_class)
    Fluidics_Class = getattr(module, fluidics_class)
    self = Fluidics_Class(gui=False)
    while True:
        self.run()


    