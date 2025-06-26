## Pump Class
Pump has three key properties: `direction`, `volume` and `speed` . 
- `direction`: The direction for pumping the fluid.
When set to `Forward`, the pump attempts to inject fluid into the chamber.
When set to `Reverse`, the pump attempts to withdraw fluid from the chamber.
When set to `Undefined`, the pump is idle. We set `direction` to `Undefined` to stop the pump after it finishes one injecting/withdrawing.
- `volume`: The amount of liquid to be pumped, in the unit of mL.
- `speed`: The speed at which the liquid is pumped, in the unit of mL/s.
## SyringePump Class
In the real setup, one syringe pump is used for the pumping of fluid. The syring pump is under the direct control of Arduino. 
Commands can be sent from the computer by writing serial message with a specific format. 
The format of the message is `@{direction}%{speed}_{duration}$!`: 
- `direction` is abbreviated by `Forward`->`F`,`Reverse`->`R`,`Undefined`->`U` to minimze RAM consumption on Arduino.
- **Very Important**: The meaning of `speed` is changed in the context of SyringePump Class.
It means duty cycle, the percentage of time where the pump is set to be on. See next section for detailed discussion.
- `duration` (in the unit of sec) is calculated based on `volume` and `speed` (duty cycle) and the calibrated speed of the syringe pump.
For example, `@{R}%{0.75}_{5}` means pumping in the reverse direction at a 0.75 duty cycle for 5 seconds . 
### `speed` of SyringePump Class
The reason for this weird change is because we have no access to setting the speed of the syringe pump.
We can only specify its direction and how long it stays on/off. 
Therefore, we have to use duty cycle as an indirect way of adjusting speed by cycling the pump between on and off.
Theoretically, `speed` can be any number between 0 to 1, but practically, due to the way of how duty cycle is implemented in [Arduino_Syringe_V2.ino](Arduino_Syringe_V2/Arduino_Syringe_V2.ino), there are only 11 levels that makes real difference: 0, 0.1, 0.2, 0.3,...,0.9,1. Any number in between will just be rounded to the closest level. For example, 0.25 will be rounded to 0.3; 0.01 will be rounded to 0 and the pump will not pump at all.
## Further reading
- See [SyringePump_v2.py](SyringePump_v2.py) for details on how user specified properties (`direction`,`volume`,`speed`) is converted to the formatted serial message.
- See [Arduino_Syringe_V2.ino](Arduino_Syringe_V2/Arduino_Syringe_V2.ino) for details on how Arduino interpret the messages and cotrol the syringe pump.
- [SyringePump.py](SyringePump.py) is deprecated and is not used on any fluidic system.
