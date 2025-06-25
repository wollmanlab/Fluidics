# Fluidics Control for Wollmanlab
This is the python library for controlling the fludic system in Roy Wollman lab at UCLA.
## Superclasses
This library consists of four superclasses: `Pumps`, `Valves`, `Protocols`, `Fluidics` . 
The definition of `Pumps`, `Valves`, `Protocols` can be found in the folder with the corresponding name. The definition of `Fluidics` is in the root . 

`Pumps`: This superclass contains general properties and methods for the control of all types of pumps in the fluidic system. 
The control of any specific subtype of pump (e.g. syringe pump, diaphragm pump) can be further customized by inheriting this superclass . 

`Valves`: This superclass contains general properties and methods for the control of all types of valves in the fludic system.
The control of any specific subtype of valve (e.g. rotatory valve, solenoid valve) can be further customized by inheriting this superclass . 

`Protocols`: This superclass contains general properties and methods for designing a protocol. 
A protocol in the context of this resiporatory means a series of coordinated operation of one or more components (e.g. pump and/or valve).
One can also create protocols for a specific type of component by inheriting this superclass . 

`Fluidics`: This superclass contains general properties and methods for interfacing user designed protocol to the GUI and the physical fluidic system.
To set up a specific fluidic system (e.g. fluidic system for the microscope 'orange'), one can create a subcalss by inheriting this superclass (e.g. OrangeFluidics) . 
## Comments on Version
For a file with suffix _v2, _v3, ..., _vN, the latest version is always the actively used one unless otherwise specified.   
