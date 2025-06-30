# Valve class
The key attribute of Valve class is a dictionary called `current_port`. 
The idea behind this attribute is that in most cases, an instance of the Valve class is not an individual valve.
Instead, it is usually a group of valves under the control of one common driver which is then connected to a computer. 
Depending on the specific type, each valve can have certain number of ports.
Fluidics can be directed to different paths by selecting (activating) different ports on a valve.
Therefore, `current_port` is a dictionary where key is the ID of each valve in the group and value is the currently selected port of the corresponding valve . 
# ViciValve class
In the real setup, we use a group of valves from the company Vici under the control of one common driver. 
The driver is connected to a COM port on the computer.
The port of each valve can be controlled by writing formatted serial message to the driver. For example:
- `"XGOY\r"` asks the driver to select port Y on valve X.
- `"XCP\r"` asks the driver to return the current port of valve X.
# Further reading
- See [VicValve.py](VicValve.py) for details on how to communicate with the driver for controlling the valves.
