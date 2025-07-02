# Protocol Class
The Protocol Class is for writing protocols to be executed by the Fluidic Class.
The core idea of a `protocol` is that any complex process to be carried out by the fluidic system can be broken down in to a sieres of simple actions in the format of "activate port A of valve B and pump fluid of volume C in the direction D at speed E over a duration of F" . 
## Create a new protocol
Therefore, we can create a protocol by defining a corresponding method in the Protocol Class.
**Note**: a specific protocol is a **method** of the Protocol Class rather than an instance of the Protocol Class.
The method (function) takes all necessary input arguments and return a dataframe with six columns:
- `port`: A uniqe name assigned to a specific port on a specific valve.
For example, we can assign the name `DAPI` to port 2 on valve 3 which is connected to the centrifuge tube holding DAPI solution.
After assigning this name in the Fluidic Class, we can put `DAPI` in the `port column` for any action that involves port 2 on valve 3.
- `volume`: Amount of fluid to be moved in the unit of mL.
- `speed`: Relative speed of pumping the fluid. A value between 0 and 1 to indicate percentage of max speed. 1 means 100% of max speed.
- `pause`: Extra amount of buffer time to pause the system without doing anything to ensure the action is finished before moving onto the next one. 
- `direction`: The direction to move the fluid, can be `Forward` or `Reverse` or `Wait`. 
- `time_estimate`: This value is usually automatically calculated in the unit of sec using the formula: `time_estimate` = (`volume`/`speed`*`speed_conversion`)+1+`pause` 
where `speed_conversion` in the unit of sec/mL is just 1/maximum_flow_rate.
## Examples
For example, we have a simple protocol `wait` which just asks the system to wiat for certain amount of time. 
This is achived by defining a `wait` method in the Protocol Class which takes the amount of time to wait (e.g., 12 sec) as input and retunrs the following dataframe where the amount of time to wait is specified in the `pause` column:
|port|volume|speed|pause|direction|time_estimate|
|---:|---:|---:|---:|---:|---:|
|''|0|1|12|'Wait'|13|

We can also have a more complex protocol involving multiple sequential actions. For example the following one first draws 3mL of liquid from the port DAPI and then pumps this 3mL of liquid to the port Chamber_1 and then wait for 10min. (`time_estimate` is calculated with an assumed `speed_conversion` of 2 just for illustration purpose).
|port|volume|speed|pause|direction|time_estimate|
|---:|---:|---:|---:|---:|---:|
|'DAPI'|3|1|0|'Reverse'|7|
|'Chamber_1'|3|1|0|'Forward'|7|
|''|0|1|600|'Wait'|601|
## `port` and `chamber`
In practice, to maximize the throughput of the fluidic system, we frequently swicth between multiple samples during one single experiment. 
For example, when one sample is being imaged on the microscope, another sample can be washed and incubated such that it can be ready once the microscope finishes imaging the current sample. 
This leads to the concept of `chamber` where samples are split into different chambers such that in the example above, when one chamber is being imaged, the other chamber(s) can be processed by the fluidic system.

You can frequently see `chamber` appears in the [source code of the Protocol Class](Protocol.py), but we do not have a separate column dedicated to `chamber` in the dataframe.
This is because, similar to solution containers, `chamber` is also connected to a specific port on a specific valve.
One key difference is that `chamber` can also be connected to two ports, one for solution inlet and the other for solution outlet. 
This is in fact the most common setup we use becasue we connect outlets to vacuum to aspirate solution from `chamber`.
However, a `chamber` can still be referred by `port` in this case because we can just refer to one chamber by the inlet `port` for injecting solution into it and by the outlet `port` when we want to remove solution from it. 
Therefore, in protocols' dataframe, we can just refer to a `chamber` by referring to `port`(s). 

However, during documentation and coding, for added clarity, we still use `chamber` to refer to the chamber holding the samples and `port`, in most cases, refer to a solution container.
# SyringeProtocol Class: building blocks for complex protocols
Since each protocol is essentially a function returning a dataframe, an easy way to build very complex protocol based on existing protocols is to append the dataframes returned by the existing protocols. 
Therefore, multiple building-block protocols dealing with frequently encountered actions are provided in the SyringeProtocol Class, a subcalss of the Protocol Class:
- `add_liquid`: Draws liquid from a `port` and injects it into a `chamber` based on user specified settings.
- `empty_chamber`: Empty a `chamber` with vacuum or pump (rare case).
- `add_volume_single`: First `empty_chamber` and then `add_liquid`.
- `replace_volume_single`: 
