from dataclasses import dataclass, field

@dataclass
class Port:
    """
    Representation of a single port on the HSX machine
    
    Attributes:
        name: string representation of the port's given name
        position: tuple(float) containing the geometric location of the port's centroid
        diameter: float representing the actual cylindrical diameter of the port
        stated_diameter: the diameter of the port listed on documentation
        depth: float representation (placeholder)
        occupant: object currently occupying the port (default = None)
        description: string containing any additional information input by the user (default = "")
    """
    name: str
    position: tuple[float, float, float]
    diameter: float
    stated_diameter: float
    depth: float
    occupant: object | None = None
    description: str

    def install(self, occupant: object) -> None:
        if self.occupant is not None:
            raise ValueError(f"Port {self.name} is already occupied")

        self.occupant = occupant

    def uninstall(self) -> object:
        if self.occupant is None:
            raise ValueError(f"Port {self.name} is not occupied")

        occupant = self.occupant
        self.occupant = None
        return occupant

    def is_occupied(self) -> bool:
        return self.occupant is None

