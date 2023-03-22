from Pumps.Pump import *
from fractions import Fraction
class SyringePump(Pump):
    """
    """
    def __init__(self,com_port,forward=5,reverse=4,gui=False):
        super().__init__()
        self.forward = 5
        self.reverse = 4
        self.com_port = com_port
        self.speed_conversion = 1.5 # mL/s
        if not gui:
            self.serial = serial.Serial(com_port, 9600, timeout=2)

    def update_user(self,message):
        if self.verbose:
            update_user(message)

    def flow(self,volume):
        speed = self.speed
        print(speed)
        # 25% increments
        speed = float(int(speed*4))/4
        if (speed<=0):
            speed = 0.05
        elif (speed>=1):
            speed = 1.0
        print(speed)
        if self.direction=='Reverse':
            pin = self.reverse
        elif self.direction=='Forward':
            pin = self.forward
        else:
            self.update_user('Unknown Direction: ',self.direction)
            pin = 13 # LED PIN
        self.pinMode(pin,"OUTPUT")
        flow_time = self.calcualte_flow_time(volume)
        if speed ==1:
            self.digitalWrite(pin,'HIGH')
            precise_sleep(flow_time)
            self.digitalWrite(pin,'LOW')
            precise_sleep(flow_time)
        else:
            dt = 0.1 # frequency of pulses
            tot_time_per_iter = 1
            tot = int((tot_time_per_iter/dt)*1)
            n_pos = int((tot_time_per_iter/dt)*speed)
            n_neg = int((tot_time_per_iter/dt)*(1-speed))
            # print(Fraction(n_pos,tot))
            # n_neg = tot-n_pos
            # n_pos,n_neg = Fraction(n_pos,n_neg)
            completed_flow_time = 0
            flow = True
            iter = 0
            while completed_flow_time<flow_time:
                if (iter>(n_pos+n_neg))|(iter==0):
                    # Reset Loop
                    iter = 1
                    flow = True
                    self.digitalWrite(pin,'HIGH')
                elif (iter>n_pos)&(flow==True):
                    # Switch Flow to not Flow
                    flow = False
                    self.digitalWrite(pin,'LOW')
                precise_sleep(dt)
                if flow:
                    completed_flow_time+=dt
                iter+=1
            self.digitalWrite(pin,'LOW')
                
                

            


    def calcualte_flow_time(self,volume):
        flow_time = float(volume)*float(self.speed_conversion)
        return flow_time

    def digitalWrite(self, pin, val):
        """
        Sends digitalWrite command
        to digital pin on Arduino
        -------------
        inputs:
           pin : digital pin number
           val : either "HIGH" or "LOW"
        """
        if val == "LOW":
            pin_ = -pin
        else:
            pin_ = pin
        cmd_str = self.build_cmd_str("dw", (pin_,))
        try:
            # self.update_user('         '+str(cmd_str))
            self.serial.write(cmd_str)
            self.serial.flush()
        except Exception as e:
            self.update_user(e)
            self.update_user('Failed to set pin.')
            pass

    def pinMode(self, pin, val):
        """
        Sets I/O mode of pin
        inputs:
           pin: pin number to toggle
           val: "INPUT" or "OUTPUT"
        """
        if val == "INPUT":
            pin_ = -pin
        else:
            pin_ = pin
        cmd_str = self.build_cmd_str("pm", (pin_,))
        try:
            self.serial.write(cmd_str)
            self.serial.flush()
        except Exception as e:
            self.update_user(e)
            self.update_user('SETUP Failed.')
            pass

    def build_cmd_str(self,cmd, args=None):
        """
        Build a command string that can be sent to the arduino.
        Input:
            cmd (str): the command to send to the arduino, must not
                contain a % character
            args (iterable): the arguments to send to the command
        @TODO: a strategy is needed to escape % characters in the args
        """
        if args:
            args = '%'.join(map(str, args))
        else:
            args = ''

        message = "@{cmd}%{args}$!".format(cmd=cmd, args=args)
        return bytes(message, 'utf-8')

        


    


    


