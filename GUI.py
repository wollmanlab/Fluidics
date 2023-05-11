# TO RUN GUI
#   $ C:\Users\wollmanlab\miniconda3\envs\py37\python.exe C:\GitRepos\Fluidics\GUI.py -f DevFluidics_v2
#   $ C:\Users\wollmanlab\miniconda3\envs\py37\python.exe C:\GitRepos\Fluidics\Fluidics.py -f DevFluidics_v2

# In the above code, you initialize the Fluidics executable and then overwrite the fluidics class with details from 
# the file that follows '-f', so in this case DevFluidics_v2 contains the details of our syringe pump and comports


import tkinter as tk
from tkinter import ttk
import threading
import socket
from fileu import *
import os
import time
import argparse
import importlib
import math

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fluidics_class", type=str, dest="fluidics_class", default="Fluidics", action='store', help="Which Fluidics Class to use")
    args = parser.parse_args()

class GUI(tk.Frame):
    def __init__(self, master=None,fluidics_class='Fluidics'):
        super().__init__(master)
        self.simulate = False
        self.busy = False
        self.verbose = True
        self.master = master
        self.master.geometry("400x250")
        self.master.title("Flow Communication")
        self.grid()

        module = importlib.import_module(fluidics_class)
        Fluidics = getattr(module, fluidics_class)
        self.Fluidics = Fluidics(gui=True)
        self.ports = [i for i in self.Fluidics.Valve_Commands.keys()]
        self.protocols = [i for i in self.Fluidics.Protocol.protocols.keys()]
        self.chambers = [i for i in self.Fluidics.Valve_Commands.keys() if len(i)==1]
        self.chambers.append('Waste')
        self.other = ""
        self.extra = ""

        self.ports.insert(0,"")
        self.protocols.insert(0,"")

        self.ports.insert(0,"")
        self.protocols.insert(0,"")

        self.running = False
        self.flow_thread = None

        self.start_button_text = 'Start'
        self.running_label_text = ""
        self.update_label_text = ""

        
        
        self.create_widgets()

    def update_user(self,message,level=20):
        if self.verbose:
            self.Fluidics.update_user(message,level=level,logger='GUI')
            
    def create_widgets(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.master.tk_setPalette( "#555555" )
        self.style.configure("TLabel", foreground="white", background="gray30")
        self.style.configure("TCheckbutton", foreground="white", background="gray30")
        self.style.configure("TEntry", foreground="white", background="gray30")
        self.style.configure("TButton", foreground="white", background="gray20", activebackground="gray40")

        # Protocol dropdown
        self.protocol_label = ttk.Label(self, text="Protocol:")
        self.protocol_label.grid(row=0, column=0, pady=10)
        self.protocol_var = tk.StringVar(self)
        self.protocol_dropdown = ttk.OptionMenu(self, self.protocol_var, *self.protocols)
        self.protocol_dropdown.grid(row=0, column=1)

        # Port dropdown
        self.port_label = ttk.Label(self, text="Ports:")
        self.port_label.grid(row=1, column=0, pady=10)
        self.port_var = tk.StringVar(self)
        self.port_dropdown = ttk.OptionMenu(self, self.port_var, *self.ports)
        self.port_dropdown.grid(row=1, column=1)

        # Volume text input
        self.extra_label = ttk.Label(self, text="Extra:")
        self.extra_label.grid(row=2, column=0, pady=10)
        self.extra_entry = ttk.Entry(self, foreground="black")
        self.extra_entry.grid(row=2, column=1)
        
        # Chambers checklist
        self.chamber_label = ttk.Label(self, text="Chambers:")
        self.chamber_label.grid(row=0, column=3)
        self.chamber_vars = []
        row_ticker = 0
        column_ticker = 0
        max_columns = 3
        for i in range(len(self.chambers)):
            if column_ticker>=max_columns:
                column_ticker = 0 
                row_ticker += 1
            self.chamber_vars.append(tk.BooleanVar(self))
            self.chamber_vars[i].set(False)
            ttk.Checkbutton(self, text=self.chambers[i], variable=self.chamber_vars[i]).place(x=250+(column_ticker*25),y=30+(20*row_ticker))
            column_ticker+=1
        # Start/Stop button
        self.start_button = ttk.Button(self, text="Start", command=self.send_communication)
        self.start_button.grid(row=3, column=0)
        # Simulate button
        self.simulate_button = ttk.Button(self, text="Simulate", command=self.simulate_communication)
        self.simulate_button.grid(row=4, column=0)

        # Make space for non grid items
        for i in range(20):
            BR= ttk.Label(self, text="")
            BR.grid(row=10+i, column=10+i)

        # # Running label
        self.running_label = ttk.Label(self, text="")
        self.running_label.place(x=50,y=175)

        # # Notifications label
        self.update_label = ttk.Label(self, text="")
        self.update_label.place(x=50,y=200)
    
        self.protocol_var.set('')
        self.port_var.set('')
        self.extra_entry.delete(0, tk.END)
        for i in range(len(self.chambers)):
            self.chamber_vars[i].set(False)
        start = time.perf_counter()
        while True:
            if time.perf_counter()-start>1:
                self.read_communication()
            precise_sleep(0.1)
            self.master.update()

    def update_labels(self,labels_dict):
        self.update_labels_later()

    def update_labels_later(self):
        # self.update_user('update_labels')
        labels_dict = self.labels()
        self.start_button.config(text=labels_dict['start_button_text'])
        self.running_label.config(text=labels_dict['running_label_text'])
        self.update_label.config(text=labels_dict['update_label_text'])
        self.master.update()

    def labels(self):
        labels_dict = {
            'start_button_text':self.start_button_text,
            'running_label_text':self.running_label_text,
            'update_label_text':self.update_label_text
        }
        return labels_dict

    def read_communication(self):
        if not self.busy:
            current_message = self.Fluidics.read_communication()
            if 'Running' in current_message:
                self.busy = True
                self.start_button_text = 'Running'
                self.running_label_text = current_message.split(':')[-1]
                self.update_label_text = 'Executing Command From File'
                self.update_labels(self.labels())
                self.wait_until_message(['Finished'],max_wait_time=60*5)
                self.start_button_text = 'Start'
                self.running_label_text = ""
                self.update_label_text = ""
                self.update_labels(self.labels())
                self.busy = False
            elif ('Available' in current_message)|('Finished' in current_message):
                self.start_button_text = 'Start'
                self.running_label_text = ""
                self.update_label_text = ""
                self.update_labels(self.labels())
                self.busy = False
        self.master.update()
        precise_sleep(0.1)

    def simulate_communication(self):
        self.simulate = True

        self.send_communication()

        self.simulate = False

    def send_communication(self):
        # Get selected protocol
        if self.protocol_var.get() !='':
            self.busy = True
            self.protocol = self.protocol_var.get()
            self.chamber = '['+''.join([self.chambers[i]+',' for i in range(len(self.chambers)) if self.chamber_vars[i].get()])[:-1]+']'
            self.port = self.port_var.get()
            self.extra = self.extra_entry.get()
            if self.simulate:
                self.extra = self.extra+'!'
            if len(str(self.extra))>0:
                message ='Command:'+self.protocol+'*'+''.join(self.chamber)+'*'+self.port + '+' + str(self.extra)
            else:
                message ='Command:'+self.protocol+'*'+''.join(self.chamber)+'*'+self.port
            
            # Check Availability
            self.update_user('Checking Device Availability')
            self.start_button_text = 'Running'
            self.running_label_text = message
            self.update_label_text = "Checking Device Availability"
            self.update_labels(self.labels())
            self.wait_until_message(['Available','Finished'],max_wait_time=60*5)

            # Send Message
            self.update_user('Communicating with Device:'+message)
            self.update_label_text = "Communicating with Device"
            self.update_labels(self.labels())
            self.Fluidics.update_communication(message)
            
            # Block until Started Error if taking too long
            self.update_user('Checking if Device is Reponsive')
            self.update_label_text = "Checking if Device is Reponsive"
            self.update_labels(self.labels())
            self.wait_until_message(['Running'],max_wait_time=60*5)
            
            # Block until Done
            self.update_user('Waiting Until Protocol is Complete')
            self.update_label_text = "Waiting Until Protocol is Complete"
            self.update_labels(self.labels())
            self.wait_until_message(['Finished'],max_wait_time=60*5)

            # Done
            self.busy = False
            self.update_user('Protocol is Complete')
            self.start_button_text = "Start"
            self.running_label_text = ""
            self.update_label_text = ""
            self.update_labels(self.labels())

    def wait_until_message(self,messages,max_wait_time=60*5):
        start = time.perf_counter()
        ready = False
        while (not ready)|(time.perf_counter()-start>max_wait_time):
            current_message = self.Fluidics.read_communication()
            for message in messages:
                if message in current_message:
                    print(current_message)
                    ready = True
            self.master.update()
            precise_sleep(0.05)
        if (time.perf_counter()-start>max_wait_time):
            raise('Timeout')

if __name__ == '__main__':

    fluidics_class = args.fluidics_class
    root = tk.Tk()
    app = GUI(root,fluidics_class=fluidics_class)
