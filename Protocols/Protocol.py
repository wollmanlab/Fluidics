import pandas as pd
from fileu import update_user
class Protocol:
    def __init__(self):
        self.verbose=True
        self.protocols = {}

    def update_user(self,message,level=20):
        if self.verbose:
            update_user(message,level=level,logger=None)
            
    def get_steps(self,protocol,chambers,other):
        """ OVERWRITE"""

    def format(self,port='A',volume=0,speed=0,pause=0,direction='Forward'):
        return pd.DataFrame([port,volume,speed,pause,direction],index = ['port','volume','speed','pause','direction']).T