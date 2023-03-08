import tkinter as tk
from tkinter import ttk
import threading
from RamboFluidics import RamboFluidics as Fluidics

class GUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("300x200")
        self.master.title("Flow Control")
        self.grid()

        self.Fluidics = Fluidics(True)
        self.ports = [i for i in self.Fluidics.Valve_Commands.keys()]
        # self.ports = ["Port 1", "Port 2", "Port 3"]
        self.protocols = [i for i in self.Fluidics.Protocol.protocols.keys()]#['Hybe','Strip','Image','Clear','Valve','Flush','Valve']
        self.chambers = [i for i in self.Fluidics.Valve_Commands.keys() if len(i)==1]
        self.other = ""

        self.running = False
        self.flow_thread = None

        self.create_widgets()

        # Apply dark theme
        self.style = ttk.Style()
        self.style.theme_use("clam")
        root.tk_setPalette( "#555555" )
        self.style.configure("TLabel", foreground="white", background="gray30")
        self.style.configure("TCheckbutton", foreground="white", background="gray30")
        self.style.configure("TEntry", foreground="white", background="gray30")
        self.style.configure("TButton", foreground="white", background="gray20", activebackground="gray40")


    def create_widgets(self):
        # Protocol dropdown
        self.protocol_label = ttk.Label(self, text="Protocol:")
        self.protocol_label.grid(row=0, column=0)
        self.protocol_var = tk.StringVar(self)
        self.protocol_dropdown = ttk.OptionMenu(self, self.protocol_var, *self.protocols)
        self.protocol_dropdown.grid(row=1, column=0)

        # Chambers checklist
        self.chamber_label = ttk.Label(self, text="Chambers:")
        self.chamber_label.grid(row=0, column=1)
        self.chamber_vars = []
        for i in range(len(self.chambers)):
            self.chamber_vars.append(tk.BooleanVar(self))
            self.chamber_vars[i].set(False)
            ttk.Checkbutton(self, text=self.chambers[i], variable=self.chamber_vars[i]).grid(row=i+1, column=1)

        # Other text input
        self.other_label = ttk.Label(self, text="Other:")
        self.other_label.grid(row=0, column=2)
        self.other_entry = ttk.Entry(self, foreground="black")
        self.other_entry.grid(row=1, column=2)

        # Start/Stop button
        self.start_button = ttk.Button(self, text="Start", command=self.toggle_flow)
        self.start_button.grid(row=2, column=2, columnspan=2,rowspan=2)

        # Port dropdown
        self.port_label = ttk.Label(self, text="Ports:")
        self.port_label.grid(row=3, column=0)
        self.port_var = tk.StringVar(self)
        self.port_dropdown = ttk.OptionMenu(self, self.port_var, *self.ports)
        self.port_dropdown.grid(row=4, column=0)

        # Start/Stop button
        self.change_port_button = ttk.Button(self, text="Change Port", command=self.change_port)
        self.change_port_button.grid(row=4, column=2, columnspan=2,rowspan=2)

        # # Running label
        self.running_label = ttk.Label(self, text="")
        self.running_label.grid(row=6, column=2, columnspan=2)

    def toggle_flow(self):
        # Start the flow function
        self.running = True
        self.start_button.config(text="Running")

        # Get selected protocol
        self.protocol = self.protocol_var.get()

        # Get selected chambers
        self.chamber = '['+''.join([self.chambers[i]+',' for i in range(len(self.chambers)) if self.chamber_vars[i].get()])[:-1]+']'

        # Get other text input
        self.other = self.other_entry.get()

        # Execute flow function in a separate thread
        self.flow_thread = threading.Thread(target=self.flow)
        self.flow_thread.start()

    def change_port(self):
        import time
        time.sleep(5)

        print(f"Protocol: {self.port_var.get()}")

    def flow(self):
        # Simulate a long-running task
        import time

        print(f"Protocol: {self.protocol}")
        print(f"Chambers: {self.chamber}")
        print(f"Other: {self.other}")

        self.running_label.config(text=self.protocol+'_'+''.join(self.chamber)+'_'+self.other)
        time.sleep(5)
        self.running = False
        self.flow_thread = None

        # Reset the start/stop button and running label
        self.start_button.config(text="Start")
        self.running_label.config(text="")

if __name__ == '__main__':
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
