## Pump Class
Pump has three key properties: `direction`, `volume` and `speed` . 
- `direction`: The direction for pumping the fluid.
When set to `Forward`, the pump attempts to inject fluid into the chamber.
When set to `Reverse`, the pump attempts to withdraw fluid from the chamber.
When set to `Undefined`, the pump does nothing.
- `volume`: The amount of liquid to be pumped, in the unit of mL.
- `speed`: The speed at which the liquid is pumped, in the unit of mL/s.
## SyringePump Class
In the real setup, one syringe pump is used for the pumping of fluid. The syring pump is under the direct control of Arduino. 
Commands can be sent from the computer by writing serial message with a specific format. 
The format of the message is `@{direction}%{speed}_{duration}$!`: 
- `direction` is abbreviated by `Forward`->`F`,`Reverse`->`R`,`Undefined`->`U` to minimze RAM consumption on Arduino.
- **Very Important**: The meaning of `speed` is changed in the context of SyringePump Class.
It means duty cycle, the percentage of time where the pump is working. Therefore, `speed` should be a number between 0 and 1.
The reason for this weird change is because we have no access to setting the speed of the syringe pump.
We can only specify its direction and how long it stays on/off.
- `duration` (in the unit of sec) is calculated based on `volume` and `speed` (duty cycle) and the calibrated speed of the syringe pump.
For example, `@{R}%{0.75}_{5}` means pumping in the reverse direction at a 0.75 duty cycle for 5 seconds . 

See [SyringePump_v2.py](SyringePump_v2.py) for details on how user specified properties (`direction`,`volume`,`speed`) is converted to the formatted serial message.
See [Arduino_Syringe_V2.ino](Arduino_Syringe_V2/Arduino_Syringe_V2.ino) for details on how Arduino interpret the messages and cotrol the syringe pump.
