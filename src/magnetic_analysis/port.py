from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import numpy as np

@dataclass
class Port:
    """
    Representation of a single port on the HSX machine
    
    Attributes:
        name: string representation of the port's given name
        position: tuple(float) containing the geometric location of the port's centroid
        diameter: float representing the actual cylindrical diameter of the port
        shape: string representation of the port's shape (generally circular)
        stated_diameter: the diameter of the port listed on documentation
        depth: float representation (placeholder)
        occupant: object currently occupying the port (default = None)
        description: string containing any additional information input by the user (default = "")
    """
    name: str
    position: np.ndarray
    normal: np.ndarray
    diameter: float = 0.076
    shape: str = "circular"
    stated_diameter: float = 0.076
    depth: float = 0.0
    occupant: Optional[Any] = None
    description: str = ""

    def __post_init__(self):
        self.position = np.asarray(self.position, dtype=float)
        self.normal = np.asarray(self.normal, dtype=float)
        norm = np.linalg.norm(self.normal)
        if norm > 0:
            self.normal = self.normal / norm

    # =========================================================================
    # Unit Convenience Properties (Imperial / US Customary)
    # =========================================================================

    @property
    def diameter_inches(self) -> float:
        """Returns port diameter in inches."""
        return self.diameter / 0.0254

    @property
    def depth_inches(self) -> float:
        """Returns port depth in inches."""
        return self.depth / 0.0254

    @property
    def nominal_flange_size(self) -> str:
        """
        Maps the metric diameter to standard ConFlat (CF) hardware names
        used in the HSX laboratory.
        """
        d_in = self.diameter_inches
        if 2.5 <= d_in <= 3.0:
            return '2-3/4" CF'
        elif 4.0 <= d_in <= 5.0:
            return '4-1/2" CF'
        elif 5.5 <= d_in <= 6.5:
            return '6" CF'
        elif 7.5 <= d_in <= 8.5:
            return '8" CF'
        return f'{d_in:.2f}" Custom'
    
    # =========================================================================
    # Occupancy
    # =========================================================================

    def install(self, occupant: object) -> None:
        if self.occupant is not None:
            raise ValueError(f"Port {self.name} is already occupied by {self.occupant}")
        self.occupant = occupant

    def uninstall(self) -> Any:
        if self.occupant is None:
            raise ValueError(f"Port {self.name} is not occupied")
        occupant = self.occupant
        self.occupant = None
        return occupant

    def is_occupied(self) -> bool:
        return self.occupant is not None

