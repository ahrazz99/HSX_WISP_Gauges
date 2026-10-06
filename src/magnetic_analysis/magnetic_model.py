
import numpy as np
from flare import model
from flare.analysis import bfield
from flare.analysis import fieldline_trace
from moose import geometry
from pathlib import Path


class MagneticModel:
    """
    This class generates a builds a magnetic model for a given configuration mesh from FLARE/EMC3-EIRENE
    
    Attributes:
        model: the model name 
        path: a Path object for the model path
        __model_loaded: internal boolean for if the model is loaded. 
    """
    def __init__(self, model_name, model_path:Path):
        self.model = model_name
        self.path = model_path
        self.__model_loaded = False

    def load_model(self):
        """
        Loads the magnetic model for the MagneticModel object based on the given model path

        Raises:
            Exception thrown by flare for the model.load function.
        """
        try:
            model.load(str(self.path))
        except Exception as e:
            print(e)
        else:
            self.__model_loaded = True
        

    def remove_model(self):
        """
        Unloads the currently loaded magnetic model.
        
        Raises:
            Runtime error if there is not model loaded.
        """
        if not self.__model_loaded:
            raise RuntimeError("The magnetic model must be loaded with the load_model function to remove a model.")
        model.free()
        self.__model_loaded = False

    def calculate_bfield(self, point:tuple[float,float,float]) -> float:
        """
        Calculates the bfield at a given point for the magnetic field as 
        
        Args:
            point: tuple containing the location data to calculate the bfield for. 
        
        Returns:
            the bfield value as a float.

        Raises:
            A runtime error if the magnetic model is not yet loaded.
        """
        if not self.__model_loaded:
            raise RuntimeError("The magnetic model must be loaded with the load_model function to calculate the bfield")
        return bfield.eval(point)

    def calculate_fieldline_forward(self, 
                                    initial_position:tuple[float,float,float], 
                                    direction:int,
                                    step_size:float,
                                    num_steps:int,
                                    beyond_boundary:bool,
                                    coordinate_system:str,
                                    angular_coord_units:str):
        """
        Calculates the field lines for a given point traced around HSX based on the loaded magnetic configuration
        
        Args:
            initial_position: tuple of 3 floats representing the starting position
            direction: integar (+/- 1) for the direction of the field line tracing
            step_size: float representing the size of steps to take while calculating the field lines
            num_steps: total number of steps to take. total distance would be step_size*num_steps
            beyond_boundary: boolean for if the calculations should end at the boundary of the system
            coordinate_system: string for the coordinate system for field line trace calculation. Must be cylindrical, cartesian, or toroidal
            angular_coord_units: string for the angular coordinates. Must be rad or deg
        
        Returns:
            x: 3-D array with the coordinates of the nodes along the traced field lines
            s: 1-D array of size x.shape[1] with the arc lengths for x
            bounded: boolean representing if the field line connects to the boundary
        
        Raises:
            A runtime error if the magnetic model is not yet loaded.
            Any other errors associated with the fieldline_trace function from FLARE.
        """
        
        if not self.__model_loaded:
            raise RuntimeError("The magnetic model must be loaded with the load_model function to calculate the strikelines")
        x, s, bounded = fieldline_trace(x0=initial_position,
                                        idir=direction,
                                        ds=step_size,
                                        nsteps=num_steps,
                                        stop_at_boundary=beyond_boundary,
                                        coordinates=coordinate_system,
                                        angular_units=angular_coord_units)
        return x, s, bounded
        