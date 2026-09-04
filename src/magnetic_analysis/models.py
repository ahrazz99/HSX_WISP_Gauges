"""
This file contains class data
"""

#Imports
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Union, Optional
from pathlib import Path
import numpy as np



"""
Port Class
    - This class is a dataclass primarily to store and hold data for a singular port on HSX
    - Each port will have 7 other ports are symmetric locations around the HSX machine.
"""
@dataclass
class Port:
    name: str
    position: np.ndarray
    normal: np.ndarray
    shape: str = "circular"
    dimensions: Dict[str, float] = field(default_factory=dict)

"""
This class manages the ports for HSX.
It assumes ports obey symmetry across a quadrant and that each quadrant is then 4-fold symmetric about the geometric center of HSX.
The port manager will hold a dictionary of ports for 1 octant and can be asked to pull the associated port for that octant or any of the other
    octants in HSX. 

Future idea is to add methods to manage occupied ports and nonsymmetric ports as necessary
"""
class HSXPortManager:
    OCTANTS = ["A", "AP", "B", "BP", "C", "CP", "D", "DP"]

    """
    object constructor
    """
    def __init__(self):
        self.base_octant_ports: Dict[str, Port] = {}

    """
    Port registration for base octant
    """
    def add_base_port(self, port: Port) -> None:
        self.base_octant_ports[port.name] = port

    """
    Compute 3x3 transformation matrix for a target octant
    """
    def _get_transformation_matrix(self, octant: str) -> np.ndarray:
        # Test for 
        if octant not in self.OCTANTS:
            raise ValueError(f"Invalid octant '{octant}'. Must be one of {self.OCTANTS}.")

        # Extract field period index (A = 0, B = 1, C = 2, D = 3)
        field_period = ord(octant[0]) - ord('A')
        angle = field_period * (np.pi / 2.0) #90 degrees per field period

        # 1. Base Z-axis rotation matrix for 4-fold symmetry
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        r_z = np.array([
            [cos_a, -sin_a, 0],
            [sin_a,  cos_a, 0],
            [    0,      0, 1]
        ])

        # 2. Apply stellarator symmetry inversion if prime (P) octant
        if "P" in octant:
            # Stellarator inversion across half-period (flips Z and Y relative to field period access)
            stellarator_flip = np.array([
                [1,  0,  0],
                [0, -1,  0],
                [0,  0, -1]
            ])
            return r_z @ stellarator_flip

        # Return unflipped r_z
        return r_z

    """Returns the transformed (position, normal) vectors for a port in a specific octant."""
    def get_port_location(self, port_name: str, octant: str = "A") -> Tuple[np.ndarray, np.ndarray]:
        if port_name not in self.base_octant_ports:
            raise KeyError(f"Port '{port_name}' not defined in base octant.")

        # Pull base port location
        base_port = self.base_octant_ports[port_name]

        # Pull transform required for requested port (if in base octant, this transform will be the identity matrix)
        transform = self._get_transformation_matrix(octant)

        # Apply transformation matrix to position and orientation vectors
        transformed_pos = transform @ base_port.position
        transformed_norm = transform @ base_port.normal

        # Return values
        return transformed_pos, transformed_norm

"""
Magnetic Model class
Encapsulates the magnetic configuration state and vectorized field evaluation
"""
class MagneticModel:

    # HSX Configuration Presets
    CONFIG_PRESETS = {
        "QHS": {"main_scale": 1.0, "aux_scale": 0.0},
        "HILL": {"main_scale": 1.0, "aux_scale": 0.10},
        "WELL": {"main_scale": 1.0, "aux_scale": -0.10},
        "MIRROR": {"main_scale": 1.0, "aux_scale": 0.0, "mirror_scale":0.20}
    }

    def __init__(
            self,
            grid_path: Union[str, Path],
            config_name: str = "QHS",
            custom_scales: Optional[Dict[str, float]] = None
    ):
        self.grid_path = Path(grid_path)
        self.config_name = config_name.upper()

        #Check that grid path is valid
        if not self.grid_path.exists():
            raise FileNotFoundError(f"Magnetic grid file missing: {self.grid_path}")

        # Coil scaling factors based on preset or custom dictionary
        if custom_scales is not None:
            self.coil_scales = custom_scales
        elif self.config_name in self.CONFIG_PRESETS:
            self.coil_scales = self.CONFIG_PRESETS[self.config_name]
        else:
            raise ValueError(f"Unknown config '{config_name}'. Choose from {list(self.CONFIG_PRESETS.keys())}")

        self._grid_data = self._load_grid()

    """
    Loads and caches magnetic grid data (.mgrid or binary array) into memory
    """
    def _load_grid(self) -> Dict[str, np.ndarray]:
        # Replace placeholder with actual file parsing (e.g., scipy.io.netcdf, h5py, or numpy)
        return {"path": str(self.grid_path)}

    """
    Evaluates B = (Bx, By, Bz) in Tesla for spatial coordinates.

    Parameters
    -------------
    points : np.ndarray
        Array of shape (3,) or (N, 3) containing (x, y, z) coordinates

    Returns
    -------------
    np.ndarray
        magnetic field vectors matching input shape (3,) or (N, 3)
    """
