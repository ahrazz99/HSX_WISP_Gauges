from typing import Dict, List, Tuple, Union, Optional
from pathlib import Path
import json
import numpy as np

#Internal imports
from magnetic_analysis.port import Port
from util.geometry import HSX_OCTANTS, get_hsx_octant_transform
from util.io import load_base_octant_ports

# Suffix inversion for prime octants due to vertical Z-flip
PRIME_SUFFIX_MAP = {
    "TT": "BB",
    "MT": "MB",
    "MM": "MM",
    "MB": "MT",
    "BB": "TT",
    "IN": "IN",
}

class PortManager:
    """
    Contains and manages all ports for a given instance of the HSX machine
    
    Attributes:
        ports: dictionary containing names and the associated port objects for a given port

    """
    OCTANTS = ["A", "AP", "B", "BP", "C", "CP", "D", "DP"]

    def __init__(self):
        self.base_octant_ports: Dict[str, Port] = {}
        self.ports: Dict[str, Port] = {}

    @classmethod
    def from_json(cls, json_path: Path) -> "PortManager":
        """Factor constructor that initializes and populates all 8 octants from JSON"""
        manager = cls()
        manager.load_base_octant_json(json_path)
        return manager

    def load_base_octant_json(self, json_path: Path) -> None:
        """Loads base octant ports via util.io and expands symmetry across all octants"""
        self.base_octant_ports = load_base_octant_ports(json_path)
        self.generate_symmetric_ports()

    def generate_symmetric_ports(self) -> None:
        """
        Applies symmetry transformations from util.geometry to base_octant_ports
        and populates lal ports across octants A through DP into self.ports.
        """
        if not self.base_octant_ports:
            raise RuntimeError("No base octant ports available to generate symmetry.")

        for octant in HSX_OCTANTS:
            transform = get_hsx_octant_transform(octant)
            for base_id, base_port in self.base_octant_ports.items():
                full_name = f"{octant}{base_id.replace('_', '')}"
                
                new_pos = transform @ base_port.position
                new_norm = transform @ base_port.normal

                # Retain existing occupant if port was already occupied
                existing_occupant = None
                if full_name in self.ports and self.ports[full_name].is_occupied():
                    existing_occupant = self.ports[full_name].occupant

                self.ports[full_name] = Port(
                    name=full_name,
                    position=new_pos,
                    normal=new_norm,
                    shape=base_port.shape,
                    diameter=base_port.diameter,
                    depth=base_port.depth,
                    occupant=existing_occupant,
                )

    # ==============================================================================
    #   Port Management and Inventory Methods
    # ==============================================================================

    def add_base_ports(self, input_ports) -> None:
        """
        Add set of port objects to the port manager object
        
        Args:
            input_ports: dictionary of ports to add to the ports dictionary
        """
        port_names = input_ports.keys()
        for name in port_names:
            self.ports[name] = input_ports[name]

    def add_single_port(self, port_name, input_port) -> None:
        """
        Add a single port object to the orts dictionary
        
        Args:
            port_name: string representation of the name of input_port
            input_port: port object 
        """
        self.ports[port_name] = input_port

    def is_port_occupied(self, port_name) -> bool:
        """
        Check if a given port is occupied
        
        Args:
            port_name: string representation of the port to check
        
        Returns:
            bool representing if the desired port is occupied. 

        Raises:
            ValueError if the port name is not in the dict of ports.
        """
        if port_name not in self.ports.keys():
            raise ValueError(f"Port {port_name} does not exist in the port manager's data.")
        return self.ports[port_name].is_occupied()

    def occupy_port(self, port_name, occupant) -> None:
        """
        Inserts an occupant into the given port
        
        Args:
            port_name: string representation of the port for the occupant
            occupant: occupant to add to the port
        
        Raises:
            ValueError if the port given does not exist or is currently occupied.
        """
        if port_name not in self.ports:
            raise ValueError(f"Port {port_name} does not exist in the port manager's data.")
        self.ports[port_name].install(occupant)

    def deoccupy_port(self, port_name) -> object:
        """
        Remove the current occupant of the port referenced by port_name
        
        Args:
            port_name: name of the port to remove the occupant from
        
        Returns:
            the occupant of the port that was removed
        
        Raises
            ValueError if the port_name given does not reference an existing port or if there is no occupant to remove
        """
        if port_name not in self.ports:
            raise ValueError(f"Port {port_name} does not exist in the port manager's data.")
        occupant = self.ports[port_name].uninstall()
        return occupant

    def get_port_geometry(self, port_name) -> tuple[tuple[float, float, float], float]:
        """
        Request data on the port position and diameter
        
        Args:
            port_name: string representation of the desired port object to pull information from
        
        Returns:
            a tuple containing the position (as a tuple) and the diameter as a float
        
        Raises
            ValueError if the given port does not exist in the database. 
        """
        if port_name not in self.ports:
            raise ValueError(f"Port {port_name} does not exist in the port manager's data.")
        return self.ports[port_name].position, self.ports[port_name].diameter

    def remove_port(self, port_name) -> Port | None:
        """
        Removes the stated port from the database.
        
        Args:
            port_name: string representation of the desired port object to remove

        Returns:
            The removed port as an object or None if the port did not exist 
        """
        if port_name not in self.ports:
            return None
        return self.ports.pop(port_name)

    def clear_ports(self) -> Dict[str, Port]:
        """
        Removes all ports from the port manager

        Returns:
            The whole port database as a dictionary
        """
        ports = self.ports
        self.ports = {}
        return ports

    def get_port(self, port_name: str) -> Port:
        """
        Retrieves a port by name.
        
        Raises:
            KeyError if the port does not exist.
        """
        if port_name not in self.ports:
            raise KeyError(f"Port '{port_name}' does not exist in the port manager.")
        return self.ports[port_name]

    def list_ports(self, octant: Optional[str] = None, occupied_only: bool = False) -> List[str]:
        """
        Returns a list of port names, optionally filtered by octant or occupancy.
        """
        names = self.ports.keys()
        if octant:
            names = [n for n in names if n.startswith(octant.upper())]
        if occupied_only:
            names = [n for n in names if self.ports[n].is_occupied()]
        return list(names)

