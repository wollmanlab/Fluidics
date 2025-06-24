# Fluidics Control for Wollmanlab
This is the python library for controlling the fludic system in Roy Wollman lab at UCLA.
## Superclasses
This library consists of three superclasses: `Pumps`, `Valves`, `Protocols`. 
The definition of each superclass can be found in the folder with the corresponding name .  

`Pumps`: This superclass contains general properties and methods for the control of all types of pumps in the fluidic system. 
The control of any specific subtype of pump (e.g. syringe pump, diaphragm pump) can be further customized by inheriting this superclass . 

`Valves`: This superclass contains general properties and methods for the control of all types of valves in the fludic system.
The control of any specific subtype of valve (e.g. rotatory valve, solenoid valve) can be further customized by inheriting this superclass . 

`Protocols`: This superclass contains general properties and methods for designing a fluidic control protocol. 
A protocol in the context of this resiporatory means the coordinated operation of different fluidic components (pump, valve, vacuum...).
One can also create protocols for a specific type of component by inheriting this superclass.
## Comments on Version
For a file with suffix _v2, _v3, ..., _vN, the latest version is always the actively used one unless otherwise specified.   
