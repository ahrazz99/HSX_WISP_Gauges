# HSX WISP Gauges

This code is designed to coordinate with FLARE and/or FIREFLY from the EMC3-EIRENE program. The code will allow the user to initialize a PortManager object that can have any and/or all of the ports from the Helically Symmetric eXperiment (HSX) for analysis in relation to a user defined magnetic field configuration (e.g. quasi-helically symmetric (QHS)).

The primary analysis will be focused on calculating strikelines/strikepoints. However, the goal of this code is flexibility, such that additional features can be added for an expanded analysis toolkit in relation to HSX.

The code does require access to EMC3-EIRENE's helper codes known as FLARE, MOOSE, and FIREFLY, therefore limiting use.

The code is currently in the process of development and has not been tested or error-checked.

## Current Project Status

- [] Implementation of v1 of class/object structure for code background processes
  - [] MagneticModel class
    - [x] Object Attribute design
    - [x] Methods
    - [x] Loading and unloading of memory handling
    - [] Biot-Savart magnetic field inputs
    - [] VMEC file inputs
  - [x] PortManager class
  - [x] Port class
  - [] PhysicalModel class
    - [] the actual code
    - [x] datafiles needed
  - [] Result class
- [] Implementation of helper/util features necessary for code
  - [] geometry.py - handles complex geometrically related calculations (like transformations)
  - [] io.py - handles input and output of data
  - [] cache.py - handles development of a cache to allow fast re-calculations of necessary data to increase efficiency
  - [] visualizer.py - handles visualization via matplotlib and pyvista
- [] Testing of class structure
- [] Design and testing of example scripts
- [] Implementation of features not currently available with FLARE (i.e. VMEC file input handling)
- [] Implementation of FIREFLY instead of FLARE