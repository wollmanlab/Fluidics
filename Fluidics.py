
import socket
import serial

class Fluidics(object):
    def __init__(self):
        self.Protocols = Protocols
        self.Pump = Pump
        self.Valve = Valve
        self.HOST = '127.0.0.1'
        self.PORT = 9500
        self.Valve_Commands = {}
        # self.socket = socket.socket('127.0.0.1',9500)

    def notify_user(self,message):
        if self.verbose:
            print(message)

    # def listen(self):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.bind((self.HOST, self.PORT))
    #         s.listen()
    #         print(f"Server is listening on {self.HOST}:{self.PORT}")
    #         while True:
    #             conn, addr = s.accept()
    #             with conn:
    #                 print(f"Connected by {addr}")
    #                 # Receive data from the client
    #                 data = conn.recv(1024)
    #                 if data:
    #                     message = data.decode()
    #                     # Interpret Message and execute protocol
    #                 # Send a response back to the client
    #                 conn.sendall(b"Available")

    def execute_protocol(self,protocol,chambers,other):
        steps = self.Protocols.get_steps(protocol,chambers,other)
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


"""

flow = Fluidics(); 
flow.socket = tcpip('127.0.0.1', 9500);


tcpServer = TCPServer(port = 9500,
                        server_name = "Fluidics",
                        verbose = True)

"""

    