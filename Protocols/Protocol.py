class Protocol:
    def __init__(self):
        self.verbose = True
        self.protocols = {}
    def get_steps(self,protocol,chambers,other):
        """ OVERWRITE"""

    def format(self,port='A',volume=0,speed=0,pause=0,direction='Forward'):
        return pd.DataFrame([port,volume,speed,pause,direction],columns = ['port','volume','speed','pause','direction'])