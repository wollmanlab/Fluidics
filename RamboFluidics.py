
class RamboFluidics(Fluidics):
    def __init__(self):
        self.Protocols = SyringeProtocols
        self.Pump = SyringePump('COM6')
        self.Valve = ViciValves('COM1')
        self.Valve_Commands = {
                                'Valve3':{'valve':2,'port':1},
                                'Waste':{'valve':2,'port':10},
                                'Valve4':{'valve':2,'port':2},
                                'Valve1':{'valve':3,'port':1},
                                'TBS':{'valve':3,'port':2},
                                'IBuffer':{'valve':3,'port':2},
                                'WBuffer':{'valve':3,'port':3},
                                'TCEP':{'valve':3,'port':4},
                                'Hybe25':{'valve':3,'port':5},
                            }
        for i in range(1,25):
            self.Valve_Commands['Hybe'+str(i)] = {'valve':hybe_valve,'port':i}
            self.Valve_Commands[str(i)] = {'valve':chamber_valve,'port':i}

    