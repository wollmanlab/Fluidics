
class Fluidics:
    def __init__(self):
        self.Protocols = Protocols
        self.Pump = Pump
        self.Valve = Valve

    def notify_user(self,message):
        if self.verbose:
            print(message)

    def execute_protocol(self,protocol,chambers,other):
        steps = self.Protocols.get_steps(protocol,chambers,other):
        if not isinstance(steps,pd.DataFrame):
            self.notify_user('Unknown Protocol: ',protocol)
        else:
            for idx,step in steps.iterrows():
                self.flow(step.port,step.volume,step.speed,step.pause,step.direction)

    def flow(self,port,volume,speed,pause,direction):
        self.set_port(port)
        self.start_flow(volume,direction,speed)
        self.sleep(pause)

    def set_port(self,command):
        if not command in self.Valve_Commands.keys():
            self.notify_user('          Unknown Tube: '+command)
        else:
            self.notify_user('          Tube: '+command)
            """ Set Port """
            self.Valve.set_port(int(self.Valve_Commands[command]['valve'])-1, int(self.Valve_Commands[command]['port'])-1)
            time.sleep(1)
            command = 'Valve'+str(self.Valve_Commands[command]['valve'])
            while command in self.Valve_Commands.keys():
                self.Valve.set_port(int(self.Valve_Commands[command]['valve'])-1, int(self.Valve_Commands[command]['port'])-1)
                command = 'Valve'+str(self.Valve_Commands[command]['valve'])
                time.sleep(1)

    def start_flow(self,volume,direction,speed):
        if volume>0:
            self.Pump.start_flow(volume,direction,speed)

    def sleep(self,t):
        if t>0:
            self.notify_user('          Wait '+str(round(t))+'s')
            for i in range(10):
                time.sleep(t/10)
                if t>0:
                    self.notify_user('          '+str(round((i+1)*10))+'% Complete')

    