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

# Adding all subdirectories in the directory of Fluidics.py to the path of python.
dir = os.path.dirname(os.path.abspath(__file__))
for file in os.listdir(dir):
    if os.path.isdir(os.path.join(dir,file)):
        sys.path.append(os.path.join(dir,file))

# An argument parser to allow user to specify which subclass of fluidics to use.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fluidics_class", type=str, dest="fluidics_class", default="Fluidics", action='store', help="Which Fluidics Class to use")
    args = parser.parse_args()
"""
    Definition of the superclass Fluidics
"""
class Fluidics(object):
    def __init__(self,gui=False):
        self.verbose=True
        self.simulate = False
        # self.Protocol = Protocol(gui=gui)
        # self.Pump = Pump(gui=gui)
        # self.Valve = Valve(gui=gui)

        self.device = self.__class__.__name__
        # file_path points to the XXXX_Staus.txt file for the communication bewteen Fluidics and other software
        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),self.device+'_Status.txt')
        self.last_message = "" # The latest message from other software
        self.Valve_Commands = {} # A dictionary for mapping port ID to specific port, see any subclass of Fluidics for examples.
        self.busy=False # Whether the fluidics is busy with running a protocol

        # self.thread = threading.Thread(target=self.run)
        # self.thread.daemon = True # without the daemon parameter, the function in parallel will continue even your main program ends
        # self.thread.start()
        if not gui:
            self.update_communication('Available')
    
    # update_user() is for writing messages to the log
    def update_user(self,message,level=20,logger='Fluidics'):
        logger = self.device +'***' + logger
        if self.verbose:
            update_user(message,level=level,logger=logger)
    
    # run() is for interpreting and running the command from other software.
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

    # read_communication() is for reading a message from the XXXX_Staus.txt file.
    def read_communication(self):
        with open(self.file_path,'r') as f:
            message = f.read()
        if self.last_message !=message:
            self.last_message = message
            self.update_user(message)
        return message

    # update_communication() is for writing to the XXXX_Staus.txt file to give other software an update, e.g. a protocol has been finished
    def update_communication(self,message):
        self.update_user(message)
        with open(self.file_path,'w') as f:
                f.write(message)

    # interpret_message() is for interpreting(spliting) the formated message read from XXXX_Staus.txt file into protocol, chambers, other
    def interpret_message(self,message):
        protocol,chambers,other = message.split('*')
        if '!' in other:
            other = other.split('!')[0]
            self.simulate = True
            self.Protocol.simulate = True
        if '+' in other:
            if other.split('+')[-1] =='':
                other = other.split('+')[0]
        chambers = chambers[1:-1].split(',')
        if 'Flush' in protocol:
            chambers = self.Valve_Commands
        if 'Prime' in protocol:
            chambers = self.Valve_Commands
        if 'Clean' in protocol:
            chambers = self.Valve_Commands
        return protocol,chambers,other

    # execute_protocol() is for executing a protocol based on the protocol, chambers, other.
    # protocol: name of the protocol to execute.
    # chambers: the chambers where the protocol should be executed.
    # other: other necessary arguments to specify the protocol
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
                        if step.pause<100:
                            precise_sleep(step.pause)
                        else:
                            t = step.pause
                            self.update_user('          Wait '+str(round(t))+'s')
                            for i in range(10):
                                precise_sleep(t/10)
                                if t>0:
                                    self.update_user('          '+str(round((i+1)*10))+'% Complete')
                    else:
                        self.flow(step.port,step.volume,step.speed,step.pause,step.direction)
            else:
                precise_sleep(1) # wait 0.5 minutes
        self.simulate = False
        self.Protocol.simulate = False

    # flow() is for executing the most basic step of a protocol (one row of the Protocol dataframe) based on the column values.
    def flow(self,port,volume,speed,pause,direction):
        self.set_port(port)
        self.start_flow(volume,direction,speed)
        self.sleep(pause)

    # set_port() is for selecting the port of a specific valve based on the port ID.
    # command: the port ID of the port to set (e.g. TBS, Hybe10, Hybe25,...)
    def set_port(self,command):
        if not command in self.Valve_Commands.keys():
            self.update_user('          Unknown Tube: '+command)
        else:
            # self.update_user('          Tube: '+command)
            # Look up and select the valve and port number corresponding to the input port ID
            self.Valve.set_port(int(self.Valve_Commands[command]['valve'])-1, int(self.Valve_Commands[command]['port'])-1)
            # This while loop to be a trick for selecting a series of valves based on special port ID naming "ValveN".
            # See NinjaFluidics.py, RonageFLuidics.py, and PurpleFluidics.py for an example where the command Valve2 can select both Valve2 and Valve3
            command = 'Valve'+str(self.Valve_Commands[command]['valve'])
            while command in self.Valve_Commands.keys():
                self.Valve.set_port(int(self.Valve_Commands[command]['valve'])-1, int(self.Valve_Commands[command]['port'])-1)
                command = 'Valve'+str(self.Valve_Commands[command]['valve'])

    # start_flow() is Pump class's start_flow with a sanity check of volume>0
    def start_flow(self,volume,direction,speed):
        if volume>0:
            self.Pump.start_flow(volume,direction,speed)

    # sleep() is for waiting for t amount of time and updating user every 10sec.
    # t: amount of time to wait in the unit of sec.
    def sleep(self,t):
        if t>0:
            self.update_user('          Wait '+str(round(t))+'s')
            for i in range(10):
                time.sleep(t/10)
                if t>0:
                    self.update_user('          '+str(round((i+1)*10))+'% Complete')

    # summarize_protocol() is for generating a summary of the steps by calculating total volume for each port and total estimated time.
    # steps: a dataframe to summarize where each row is one step
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

# Load the subclass selected by user.
if __name__ == '__main__':
    fluidics_class = args.fluidics_class
    module = importlib.import_module(fluidics_class)
    Fluidics_Class = getattr(module, fluidics_class)
    self = Fluidics_Class(gui=False)
    while True:
        self.run()


    
