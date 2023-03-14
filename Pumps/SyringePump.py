from Pumps.Pump import *
class SyringePump(Pump):
    """
    """
    def __init__(self,com_port,forward=5,reverse=4):
        self.forward = 5
        self.reverse = 4
        self.com_port = com_port
        self.serial = serial.Serial(com_port, 9600, timeout=2)

    def update_user(self,message):
        if self.verbose:
            print(message)

    def flow(self,volume):
        if self.direction=='Reverse':
            pin = self.reverse
        elif self.direction=='Forward':
            pin = self.forward
        else:
            self.update_user('Unknown Direction: ',self.direction)
            pin = 13 # LED PIN
        self.pinMode(pin,"OUTPUT")
        self.digitalWrite(pin,'HIGH')
        flow_time = self.calcualte_flow_time(volume)
        print('     Waiting '+str(int(flow_time))+'s for pump')
        time.sleep(flow_time)
        self.digitalWrite(pin,'LOW')
        time.sleep(flow_time/10)

    def calcualte_flow_time(self,volume):
        flow_time = volume
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
            # print('         '+str(cmd_str))
            self.serial.write(cmd_str)
            self.serial.flush()
        except Exception as e:
            print(e)
            print('Failed to set pin.')
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
            print(e)
            print('SETUP Failed.')
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

        


    


    


