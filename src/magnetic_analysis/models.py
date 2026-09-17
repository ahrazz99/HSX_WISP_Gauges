"""
This file contains class data
"""

#Imports
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Union, Optional
from pathlib import Path
from flare import model as flare_model
from flare.analysis import bfield as flare_bfield
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

    def __init__(self, model_path: Union[str, Path], name: str = "qhs"):
        self.model_path = Path(model_path)
        self.name = name
        self._load_model()

        #Check that grid path is valid
        if not self.model_path.exists():
            raise FileNotFoundError(f"EMC3 NetCDF Magnetic data file missing: {self.model_path}")
        
        self._grid_data = self._load_grid()


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
    def evaluate_bfield(self, points: np.ndarray) -> np.ndarray:
        pts = np.asarray(points, dtype=float)
        orig_shape = pts.shape

        # Normalize 1D (3,) inputs to 2D (1,3) for uniform processing
        if pts.ndim == 1:
            if pts.shape[0] != 3:
                raise ValueError(f"Coordinate vector must have length 3, got {pts.shape[0]}")
            pts = pts.reshape(1,3)
        elif pts.ndim != 2 or pts.shape[1] != 3:
            raise ValueError(f"Points array must have shape (N, 3), got {pts.shape}")

        # Place vector interpolation logic here (e.g. trilinear interpolation over grid)
        b_vectors = np.zeros_like(pts)

        return b_vectors.reshape(orig_shape)

    """
    Returns magnetic field strength |B| in Tesla for given coordinates.
    """
    def evaluate_magnitude(self, points: np.ndarray) -> np.ndarray:
        b_vecs = self.evaluate_bfield(points)
        return np.linalg.norm(b_vecs, axis=-1)
