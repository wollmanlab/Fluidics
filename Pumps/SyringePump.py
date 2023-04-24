from Pumps.Pump import *
from fractions import Fraction
import numpy as np
class SyringePump(Pump):
    """
    """
    def __init__(self,com_port,forward=5,reverse=4,gui=False):
        super().__init__()
        self.forward = 5
        self.reverse = 4
        self.com_port = com_port
        self.speed_conversion = 1.5 # mL/s
        self.wait_factor = 1/3
        if not gui:
            self.serial = serial.Serial(com_port, 9600, timeout=2)

    def flow(self,volume):
        self.pinMode(13,"OUTPUT")
        self.digitalWrite(13,'HIGH')

        speed = self.speed
        # print(speed)
        # 25% increments
        speed = float(int(speed*4))/4
        if (speed<=0):
            speed = 0.05
        elif (speed>=1):
            speed = 1.0
        # print(speed)
        if self.direction=='Reverse':
            pin = self.reverse
        elif self.direction=='Forward':
            pin = self.forward
        else:
            self.update_user('Unknown Direction: ',self.direction)
            pin = 13 # LED PIN
        self.pinMode(pin,"OUTPUT")
        flow_time = self.calculate_flow_time(volume)
        if speed ==1:
            self.digitalWrite(pin,'HIGH')
            precise_sleep(flow_time)
            self.digitalWrite(pin,'LOW')
            precise_sleep(flow_time*self.wait_factor) #wait for syringe to fill or empty
        else:
            dt = 0.5
            n_pos_steps = int(flow_time/dt)
            n_steps = int((flow_time/dt)/speed)
            steps = np.zeros(n_steps)
            ratio = int(n_steps/n_pos_steps)
            used_pos_steps = 0
            for s in range(steps.shape[0]):
                if s%ratio==0:
                    if used_pos_steps<n_pos_steps:
                        steps[s] = 1
                        used_pos_steps+=1

            # steps[0:int(flow_time/dt)] = 1
            # np.random.shuffle(steps)
            direction = -1
            # print(steps)
            for s in range(steps.shape[0]):
                d = steps[s]
                if d!=direction:
                    direction = d
                    # print('step',s,'direction',direction)
                    if d==1:
                        self.digitalWrite(pin,'HIGH')
                    elif d==0:
                        self.digitalWrite(pin,'LOW')
                direction = d
                precise_sleep(dt)
            self.digitalWrite(pin,'LOW')



            # dt = 0.25 # frequency of pulses
            # tot_time_per_iter = 1
            # tot = int((tot_time_per_iter/dt)*1)
            # n_pos = int((tot_time_per_iter/dt)*speed)
            # n_neg = int((tot_time_per_iter/dt)*(1-speed))
            # # print(Fraction(n_pos,tot))
            # # n_neg = tot-n_pos
            # # n_pos,n_neg = Fraction(n_pos,n_neg)
            # completed_flow_time = 0
            # flow = True
            # iter = 0
            # while completed_flow_time<flow_time:
            #     if (iter>(n_pos+n_neg))|(iter==0):
            #         # Reset Loop
            #         iter = 1
            #         flow = True
            #         self.digitalWrite(pin,'HIGH')
            #     elif (iter>n_pos)&(flow==True):
            #         # Switch Flow to not Flow
            #         flow = False
            #         self.digitalWrite(pin,'LOW')
            #     precise_sleep(dt)
            #     if flow:
            #         completed_flow_time+=dt
            #     iter+=1
            # self.digitalWrite(pin,'LOW')
        self.pinMode(13,"OUTPUT")
        self.digitalWrite(13,'LOW')

    def calculate_flow_time(self,volume):
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

        


    


    


