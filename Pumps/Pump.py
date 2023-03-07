class Pump:
    """

    """
    def __init__(self):
        self.direction = 'Forward'
        self.volume = 0
        self.speed = 0

    def notify_user(self,message):
        if self.verbose:
            print(message)

    def start_flow(self,volume,direction,speed):
        self.set_direction(direction)
        self.set_speed(speed)
        self.flow(volume)

    def set_direction(self,direction):
        self.direction = direction

    def set_speed(self,speed):
        self.speed = speed

    def flow(self,volume):
        """ OVERWRITE"""
        
        


    


    


