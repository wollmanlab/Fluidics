# Fluidics Control System

A Python-based fluidics control system for automated liquid handling in laboratory experiments. This system provides precise control over syringe pumps and multi-port valves for various protocols including hybridization, washing, and sample preparation.

## Overview

The Fluidics Control System is designed for automated liquid handling in molecular biology experiments, particularly for in situ hybridization protocols. It consists of:

- **Syringe Pump Control**: Precise volume dispensing with configurable speeds
- **Multi-port Valve Control**: Automated switching between different liquid sources
- **Protocol Management**: Pre-defined and customizable experimental protocols
- **GUI Interface**: User-friendly graphical interface for protocol execution
- **Command-line Interface**: Scriptable control for automated workflows

## System Requirements

- Python 3.7
- Windows/Linux/macOS
- Serial communication capability
- Conda package manager (recommended)

## Installation

### 1. Create Conda Environment

```bash
# Create a new conda environment with Python 3.7
conda create --name py37 python=3.7

# Activate the environment
conda activate py37
```

### 2. Install Dependencies

```bash
# Install required packages
pip install pyserial
pip install pandas
pip install numpy
```

### 3. Hardware Setup

The system requires:
- **Syringe Pump**: Connected via serial port (default: COM6)
- **Multi-port Valve**: VICI valve connected via serial port (default: COM7)
- **Arduino Controller**: For syringe pump control (see `Arduino_Code_v2.txt`)

## Configuration

### Valve Configuration

Each fluidics class defines valve commands mapping port names to valve/port combinations:

```python
self.Valve_Commands = {
    'A': {'valve': 1, 'port': 1},
    'B': {'valve': 1, 'port': 2},
    'Waste': {'valve': 1, 'port': 13},
    'TBS': {'valve': 1, 'port': 24},
    # ... additional ports
}
```

### Pump Configuration

Configure syringe pump parameters in your fluidics class:

```python
self.Pump.wait_factor = 1/2
self.Pump.speed_conversion = 1.9
self.Protocol.speed = 1
self.Protocol.closed_speed = 0.3
```

## Usage

### GUI Interface

Launch the graphical interface:

```bash
python GUI.py -f DevFluidics_v2
```

The GUI provides:
- Protocol selection dropdown
- Port selection for liquid sources
- Chamber selection checkboxes
- Volume and parameter input
- Start/Stop controls
- Simulation mode

### Command Line Interface

Run protocols directly from command line:

```bash
python Fluidics.py -f DevFluidics_v2
```

### Available Protocols

The system includes numerous pre-defined protocols:

- **Hybe**: Hybridization protocol
- **Strip**: Stripping protocol
- **Clean**: System cleaning
- **Prime**: System priming
- **Valve**: Direct valve control
- **ReverseFlush**: Reverse flushing
- **Storage2Gel**: Storage to gel transfer
- **Gel2Hybe**: Gel to hybridization transfer
- **Hybe2Image**: Hybridization to imaging transfer
- **PrepSample**: Sample preparation
- **dendcycle**: Dendrimer cycling
- **bdna**: Bridge amplification

## Architecture

### Core Components

1. **Fluidics.py**: Main control class with protocol execution logic
2. **Pumps/**: Pump control modules
   - `Pump.py`: Base pump class
   - `SyringePump_v2.py`: Syringe pump implementation
3. **Valves/**: Valve control modules
   - `Valve.py`: Base valve class
   - `ViciValve.py`: VICI valve implementation
4. **Protocols/**: Protocol definitions
   - `Protocol.py`: Base protocol class with all protocol methods
   - `SyringeProtocol.py`: Syringe-specific protocols

### Fluidics Classes

Different fluidics configurations are available:

- `DevFluidics_v2.py`: Development system configuration
- `BlueFluidics.py`: Blue system configuration
- `PurpleFluidics.py`: Purple system configuration
- `OrangeFluidics.py`: Orange system configuration
- `RedSamplePrep.py`: Red sample preparation system
- `GreenSamplePrep.py`: Green sample preparation system
- `HybeFluidics.py`: Hybridization system
- `NinjaFluidics.py`: Ninja system configuration
- `RamboFluidics.py`: Rambo system configuration
- `FutureFluidics.py`: Future system configuration

## Protocol Development

### Creating Custom Protocols

Add new protocols to `Protocols/Protocol.py`:

```python
def my_custom_protocol(self, chambers, other):
    steps = []
    # Add protocol steps
    steps.append(self.format(port='A', volume=1.0, speed=1, pause=0, direction='Forward'))
    return pd.concat(steps, ignore_index=True)
```

### Protocol Step Format

Each protocol step includes:
- `port`: Valve port identifier
- `volume`: Volume to dispense (mL)
- `speed`: Flow speed (mL/min)
- `pause`: Wait time after step (seconds)
- `direction`: Flow direction ('Forward'/'Reverse'/'Wait')

## Communication

The system uses file-based communication for external control:

- Status file: `{DeviceName}_Status.txt`
- Command format: `Command:Protocol*[Chambers]*Parameters!`

Example command:
```
Command:Hybe*[A,B,C]*600!
```

## Troubleshooting

### Common Issues

1. **Serial Connection Errors**
   - Verify COM port numbers in fluidics class
   - Check hardware connections
   - Ensure no other software is using the ports

2. **Protocol Execution Errors**
   - Verify valve commands are properly configured
   - Check that all required ports are defined
   - Ensure sufficient liquid volume in reservoirs

3. **Pump Communication Issues**
   - Verify Arduino code is uploaded correctly
   - Check serial communication parameters
   - Test with simple valve commands first

### Debug Mode

Enable verbose output by setting:
```python
self.verbose = True
```

## File Structure

```
Fluidics/
├── Fluidics.py              # Main control class
├── GUI.py                   # Graphical interface
├── Protocols/               # Protocol definitions
│   ├── Protocol.py
│   └── SyringeProtocol.py
├── Pumps/                   # Pump control modules
│   ├── Pump.py
│   ├── SyringePump.py
│   └── SyringePump_v2.py
├── Valves/                  # Valve control modules
│   ├── Valve.py
│   └── ViciValve.py
├── Pumps/Arduino_Syringe_V2/ # Arduino code
│   └── Arduino_Syringe_V2.ino
├── *Fluidics.py            # System-specific configurations
└── Setup_env.txt           # Environment setup instructions
```

## License

This project is licensed under the GPL-3.0 License - see the `gpl-3.0.txt` file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with your hardware setup
5. Submit a pull request

## Support

For technical support or questions about the fluidics system, please contact the development team or refer to the hardware documentation for your specific setup. 