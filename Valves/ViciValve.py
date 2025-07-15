from Valves.Valve import *
import time
class ViciValve(Valve):
    """
    Definition of ViciValve, a subclass of Valve.
    """
    def __init__(self,com_port,gui=False):
        super().__init__()
        self.com_port = com_port # The serial port of the valve controller on the computer
        self.current_port = {} # A dictionary for storing the currently selected port of each vicivalve.
        
        if not gui:
            self.serial = serial.Serial(port = self.com_port, 
                                    baudrate = 9600, 
                                    bytesize = serial.EIGHTBITS, #8 bits
                                    parity = serial.PARITY_NONE, 
                                    stopbits = serial.STOPBITS_ONE, 
                                    timeout = 0.1)
        self.acknowledge = " ID = "
        self.carriage_return = bytes("\r", 'utf-8') # All serial messages from Vici valve end with a utf-8 encoded carriage return.
        self.negative_acknowledge = "" # The message from the Vici valve when it cannot respond properly.
        self.read_length = 64
        self.char_offset = 97

    # set_port() selects the specified port of the specified Vici valve.
    def set_port(self, valve_ID, port_ID):
        # Send a formated serial message readable by Vici Valve to select port with port_ID on the valve with valve_ID
        valve_ID = str(valve_ID)
        port_ID = str(int(port_ID)+1)
        message = valve_ID + "GO" + port_ID + "\r"
        self.write(message)
        time.sleep(1)
        # Update the current_port dictionary
        self.current_port[valve_ID] = self.get_port(valve_ID)

    # get_port() is for getting the currently selected port of the specified Vici valve. 
    def get_port(self,valve_ID):
        message = "CP\r" # This is the serial message for Vici valve to return the current port.
        response = self.inquireAndRespond(valve_ID, message)
        if response[0] == "Negative Acknowledge":
            self.update_user("Move failed: " + str(response))
        if response[1]:
            return response[3].split(' ')[-1]
            
    #  read() reads the serial message from Vici valve and get the content before the ending marker (carriage_return).  
    def read(self):
        response = self.serial.read(self.read_length).split(self.carriage_return)[0]
        # if self.verbose:
            # self.update_user "Received: " + str((response, ""))
        return response
        
    # write() encodes the message with utf-8 and send it to the Vici valve
    def write(self, message):
        message = bytes(message, 'utf-8')
        self.serial.write(message)

    # self.inquireAndRespond() inqures the Vici valve with valve_ID with the message.
    # It returns a tuple of length 3: Type of the response, Whether the response is positive (successful), The content of the response.
    # There are two optional input dictionary and default.
    # dictionary should be a dictionary where key is the type of the response and value is the content of the response.
    # If the content of the response is not in dictionary, default is returned as type of the response.
    def inquireAndRespond(self, valve_ID, message, dictionary = {}, default = "Unknown"):
        # Send message and read response
        self.write(valve_ID + message)
        response = str(self.read())
        if len(response)>0:
            # Strip off valve id
            response = response[2:]
                
        # The case when the Vici Valve cannot respond
        if response == self.negative_acknowledge:
            return ("No Response", False, response)

        # The case when the Vici Valve responds 'Bad command'
        if 'Bad command' in response:
            # Parse provided dictionary with response
            return ("Negative Acknowledge", False, response)

        # If user provide a dictionary, map the content of the response to the corresponding type of the response.
        try:
            return_value = dictionary.get(response, default)
            if return_value == default:
                return (default, False, response)
            else:
                return (return_value, True, response)
        except:
        # Otherwise, use "Acknowledge" as the type of the response.
            return ("Acknowledge", True, response)



    


