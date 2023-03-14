import serial
import time
import pandas as pd
import numpy as np
from fileu import update_user
from Pumps.SyringePump import Pump as Pump
from Protocols.SyringeProtocol import Protocol as Protocol
from Valves.ViciValve import Valve as Valve


class Fluidics(object):
    def __init__(self):
        self.verbose=True
        self.Protocol = Protocol
        self.Pump = Pump
        self.Valve = Valve
        self.HOST = '127.0.0.1'
        self.PORT = 9500
        self.Valve_Commands = {}

    def update_user(self,message,level=20):
        if self.verbose:
            update_user(message,level=level,logger=None)

    def read_message(self,message):
        protocol,chambers,other = message.split('_')
        chambers = chambers[1:-1].split(',')
        return protocol,chambers,other

    def execute_protocol(self,protocol,chambers,other):
        steps = self.Protocol.get_steps(protocol,chambers,other)
        if not isinstance(steps,pd.DataFrame):
            self.update_user('Unknown Protocol: ',protocol)
        else:
            for idx,step in steps.iterrows():
                self.flow(step.port,step.volume,step.speed,step.pause,step.direction)

    def flow(self,port,volume,speed,pause,direction):
        self.set_port(port)
        self.start_flow(volume,direction,speed)
        self.sleep(pause)

    def set_port(self,command):
        if not command in self.Valve_Commands.keys():
            self.update_user('          Unknown Tube: '+command)
        else:
            self.update_user('          Tube: '+command)
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


"""

flow = Fluidics(); 
flow.socket = tcpip('127.0.0.1', 9500);


tcpServer = TCPServer(port = 9500,
                        server_name = "Fluidics",
                        verbose = True)

"""

    