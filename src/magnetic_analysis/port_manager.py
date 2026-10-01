from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Union, Optional
from pathlib import Path

#Internal imports
from magnetic_analysis.port import Port

class PortManager:
    """
    Contains and manages all ports for a given instance of the HSX machine
    
    Attributes:
        ports: dictionary containing names and the associated port objects for a given port

    """
    OCTANTS = ["A", "AP", "B", "BP", "C", "CP", "D", "DP"]

    def __init__(self):
        self.ports: Dict[str, Port] = {}

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

    def clear_ports(self) -> Dict[Port]:
        """
        Removes all ports from the port manager

        Returns:
            The whole port database as a dictionary
        """
        ports = self.ports
        self.ports = {}
        return ports
        


