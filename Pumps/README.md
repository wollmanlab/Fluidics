## Pump Class
Pump has two key properties: `direction`, `volume` and `speed` . 
- `direction`: The direction for pumping the fluid.
When set to `Forward`, the pump attempts to inject fluid into the chamber.
When set to `Reverse`, the pump attempts to withdraw fluid from the chamber.
When set to `Undefined`, the pump does nothing.
- `volume`: The amount of liquid to be pumped, in the unit of mL.
- `speed`: The speed at which the liquid is pumped, in the unit of mL/s.
## SyringePump Class
In the real setup, one syringe pump is used for the pumping of fluid. The syring pump is under the direct control of Arduino. 
Commands can be sent from the computer by writing serial message with a specific format. 
The format of the message is `@{direction}%{speed}_{duration}$!` where direction is abbreviated by `Forward`->`F`,`Reverse`->`R`,`Undefined`->`U`. 
For example, `@{R}%{1}_{5}` means pumping in the reverse direction at 1mL/s for 5 seconds . 

See [Arduino_Syringe_V2.ino](Arduino_Syringe_V2/Arduino_Syringe_V2.ino) for details on how Arduino interpret the messages and cotrol the syringe pump.
