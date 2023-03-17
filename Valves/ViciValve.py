from Valves.Valve import *
import time
class ViciValve(Valve):
    """

    """
    def __init__(self,com_port,gui=False):
        super().__init__()
        self.com_port = com_port
        self.current_port = {}
        
        if not gui:
            self.serial = serial.Serial(port = self.com_port, 
                                    baudrate = 9600, 
                                    bytesize = serial.EIGHTBITS, #8 bits
                                    parity = serial.PARITY_NONE, 
                                    stopbits = serial.STOPBITS_ONE, 
                                    timeout = 0.1)
        self.acknowledge = " ID = "
        self.carriage_return = bytes("\r", 'utf-8')
        self.negative_acknowledge = ""
        self.read_length = 64
        self.char_offset = 97

    def update_user(self,message):
        if self.verbose:
            update_user(message)

    def set_port(self, valve_ID, port_ID):
        valve_ID = str(valve_ID)
        port_ID = str(int(port_ID)+1)
        message = valve_ID + "GO" + port_ID + "\r"
        self.write(message)
        time.sleep(1)
        self.current_port[valve_ID] = self.get_port(valve_ID)

    def get_port(self,valve_ID):
        message = "CP\r"
        response = self.inquireAndRespond(valve_ID, message)
        if response[0] == "Negative Acknowledge":
            self.update_user("Move failed: " + str(response))
        if response[1]:
            return response[3].split(' ')[-1]

    def read(self):
        response = self.serial.read(self.read_length).split(self.carriage_return)[0]
        # if self.verbose:
            # self.update_user "Received: " + str((response, ""))
        return response

    def write(self, message):
        message = bytes(message, 'utf-8')
        self.serial.write(message)


    def inquireAndRespond(self, valve_ID, message, dictionary = {}, default = "Unknown"):
        # Write message and read response
        self.write(valve_ID + message)
        response = str(self.read())
        if len(response)>0:
            # Strip off valve id
            response = response[2:]
                
        # Check for negative acknowledge
        if response == self.negative_acknowledge:
            return ("No Response", False, response)

        if 'Bad command' in response:
            # Parse provided dictionary with response
            return ("Negative Acknowledge", False, response)

        try:
            return_value = dictionary.get(response, default)
            if return_value == default:
                return (default, False, response)
            else:
                return (return_value, True, response)
        except:
            return ("Acknowledge", True, response)



    


