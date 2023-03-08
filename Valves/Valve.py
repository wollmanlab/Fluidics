import serial
class Valve:
    """

    """
    def __init__(self):
        self.current_port = {}

    def notify_user(self,message):
        if self.verbose:
            print(message)

    def set_port(self,valve,port):
        self.current_port[valve] = port

    def get_port(self,valve):
        return self.current_port[valve]


    


    


