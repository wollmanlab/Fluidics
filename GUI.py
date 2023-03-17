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
        self.file_path = 'C:/GitRepos/Fluidics/Log.txt'
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
        self.other = ""
        self.extra = ""

        self.ports.insert(0,"")
        self.protocols.insert(0,"")

        self.ports.insert(0,"")
        self.protocols.insert(0,"")

        self.running = False
        self.flow_thread = None
        # Apply dark theme
        self.style = ttk.Style()
        self.style.theme_use("clam")
        root.tk_setPalette( "#555555" )
        self.style.configure("TLabel", foreground="white", background="gray30")
        self.style.configure("TCheckbutton", foreground="white", background="gray30")
        self.style.configure("TEntry", foreground="white", background="gray30")
        self.style.configure("TButton", foreground="white", background="gray20", activebackground="gray40")

        self.create_widgets()

        
        # self.update_log('Available')

        # self.thread = threading.Thread(target=self.send_communication)
        # self.thread.daemon = True # without the daemon parameter, the function in parallel will continue even your main program ends
        # self.thread.start()

    def update_user(self,message,level=20):
        if self.verbose:
            self.Fluidics.update_user(message,level=level)
            
    def create_widgets(self):
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
            # ttk.Checkbutton(self, text=self.chambers[i], variable=self.chamber_vars[i]).grid(row=i+4, column=1)
            ttk.Checkbutton(self, text=self.chambers[i], variable=self.chamber_vars[i]).place(x=250+(column_ticker*25),y=30+(20*row_ticker))
            column_ticker+=1
        # Start/Stop button
        self.start_button = ttk.Button(self, text="Start", command=self.send_communication)
        self.start_button.grid(row=3, column=0)

        for i in range(10):
            BR= ttk.Label(self, text="")
            BR.grid(row=10+i, column=10+i)

        # # Running label
        self.running_label = ttk.Label(self, text="")
        self.running_label.place(x=50,y=150)#.grid(row=len(self.chambers)+9, column=0, columnspan=1)

        # # Notifications label
        self.update_label = ttk.Label(self, text="")
        self.update_label.place(x=50,y=175)#.grid(row=len(self.chambers)+8, column=0, columnspan=1)
    
        # test = []
        # step = 50
        # for x in range(10):
        #     for y in range(10):
        #         temp = ttk.Label(self, text='{}x{}'.format(x*step, y*step))
        #         temp.place(x=x*step,y=y*step)
        #         test.append(temp)



        self.protocol_var.set('')
        self.port_var.set('')
        self.extra_entry.delete(0, tk.END)
        for i in range(len(self.chambers)):
            self.chamber_vars[i].set(False)

        # self.thread = threading.Thread(target=self.send_communication)
        # self.thread.daemon = True # without the daemon parameter, the function in parallel will continue even your main program ends
        # self.thread.start()

        # window_width = self.master.winfo_reqwidth()+100
        # window_height = self.master.winfo_reqheight()+100
        # self.master.geometry('{}x{}'.format(window_width, window_height))
        start = time.perf_counter()
        while True:
            if time.perf_counter()-start>1:
                self.read_communication()
            precise_sleep(0.05)
            self.master.update()

    def update_labels(self,labels_dict):
        self.update_labels_later()

    def update_labels_later(self):
        self.update_user('update_labels')
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
                # self.start_button.config(text="Running")
                # self.running_label.config(text=current_message.split(':')[-1])
                # self.update_label.config(text='Executing Command From File')
                self.wait_until_message(['Finished'],max_wait_time=60*5)
                self.start_button_text = 'Start'
                self.running_label_text = ""
                self.update_label_text = ""
                self.update_labels(self.labels())
                # self.running_label.config(text='')
                # self.update_label.config(text='')
                # self.start_button.config(text="Start")
                self.busy = False
        # root.after(1000, self.read_communication) # Every Second

    def send_communication(self):
        # Get selected protocol
        if self.protocol_var.get() !='':
            self.busy = True
            self.protocol = self.protocol_var.get()
            self.chamber = '['+''.join([self.chambers[i]+',' for i in range(len(self.chambers)) if self.chamber_vars[i].get()])[:-1]+']'
            self.port = self.port_var.get()
            self.extra = self.extra_entry.get()

            # self.protocol_var.set('')
            # self.port_var.set('')
            # self.extra_entry.delete(0, tk.END)
            # for i in range(len(self.chambers)):
            #     self.chamber_vars[i].set(False)

            if len(str(self.extra))>0:
                message ='Command:'+self.protocol+'_'+''.join(self.chamber)+'_'+self.port + '+' + str(self.extra)
            else:
                message ='Command:'+self.protocol+'_'+''.join(self.chamber)+'_'+self.port
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
    # root.after(1000, app.read_communication) # Every Second
    # root.mainloop()
