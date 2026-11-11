"""
src/util/geometry.py
Geometric Utilities, coordinate transformations, and HSX symmetry definitions.
"""

from typing import Tuple, Union
import numpy as np

#All valid HSX Octant identifiers
HSX_OCTANTS = ["A", "AP", "B", "BP", "C", "CP", "D", "DP"]

#Conversion Factors
INCHES_TO_METERS = 0.0254
METERS_TO_INCHES = 1.0 / 0.0254

def get_hsx_octant_transform(octant: str) -> np.ndarray:
    """
    Computes the 3x3 transformation matrix for a target HSX octant using 4-fold rotational symmetry
    (4 field periods) and stellarator symmetry inversions
    
    Args:
        octant: String identifier for a given octant 
    
    Returns:
        3x3 numpy array transformation matrix
        
    Raises:
        ValueError if invalid octant is input
    """

    octant = octant.upper()
    if octant not in HSX_OCTANTS:
        raise ValueError(f"Invalid Octant '{octant}'. Must be one of {HSX_OCTANTS}.")

    # Field period index: A=0, B=1, C=2, D=3 (90 degrees / pi / 2 per period)
    field_period = ord(octant[0]) - ord("A")
    angle = field_period * (np.pi / 2.0)

    cos_a, sin_a = np.cos(angle), np.sin(angle)
    r_z = np.array([
        [cos_a, -sin_a, 0.0],
        [sin_a,  cos_a, 0.0],
        [0.0,      0.0, 1.0]
    ])

    # Prime Octant ('P'): apply stellarator symmmetry inversion across half-period
    if "P" in octant:
        stellarator_flip = np.array([
            [1.0,  0.0,  0.0], 
            [0.0, -1.0,  0.0],
            [0.0,  0.0, -1.0]
        ])
        return r_z @ stellarator_flip
    return r_z


def cartesian_to_cylindrical(x: float, y: float, z: float, degrees: bool = False) ->Tuple[float, float, float]:
    """
    Converts the given 3D coordinate to cylindrical coordinates
    
    Args:
        x: float of the x coordinate
        y: float of the y coordinate
        z: float of the z coordinate
        degrees: bool indicating if the phi angle should be returned as a degree (True) or radian (False)
    
    Returns:
        Tuple containing the cylindrical coordinates as (r, z, phi)
        
    """
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    if degrees:
        phi = np.degrees(phi)
    return float(r), float(z), float(phi)

def cylindrical_to_cartesian(r: float, z: float, phi: float, degrees: bool = False) -> Tuple[float, float, float]:
    """
    Converts the given cylindrical coordinates to cartesian coordinates
    
    Args:
        r: float representation of the radial coordinate value
        z: float representation of the vertical coordinate value
        phi: float representation of the angular coordinate value
        degrees: indicates if the phi value given is in degrees (True) or radians (False)
    
    Returns:
        Tuple containing the Cartesian coordinates as (x, y, z)
        
    """
    phi_rad = np.radians(phi) if degrees else phi
    return float(r * np.cos(phi_rad)), float(r * np.sin(phi_rad)), float(z)


def angular_vector_separation(vec_a, vec_b, degrees: bool = True) -> float:
    """
    Calculates the angle between the 2 vectors
    
    Args:
        vec_a: first vector
        vec_b: second vector
        degrees: whether the resulting angle should be given in degrees (True) or radians (False)
    """
    a, b = np.asarray(vec_a, dtype=float), np.asarray(vec_b, dtype=float)
    cos_theta = np.clip(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1.0, 1.0)
    angle = np.arccos(cos_theta)
    return float(np.degrees(angle)) if degrees else float(angle)

def inches_to_meters(inches: float) -> float:
    return float(inches * INCHES_TO_METERS)

def meters_to_inches(meters: float) -> float:
    return float(meters * METERS_TO_INCHES)