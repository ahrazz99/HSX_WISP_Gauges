"""
src/magnetic_analysis/magnetic_model.py
Wraps FLARE magnetic field evaluations and fieldline tracing for HSX configurations.
"""

from pathlib import Path
from typing import Tuple, Union, Optional
import numpy as np

from flare import model
from flare.analysis import bfield
from flare.analysis import fieldline_trace
from util.process import run_isolated


def _trace_worker(
    pt: list,
    direction: int,
    ds: float,
    nsteps: int,
    stop_at_boundary: bool,
    coord_sys: str,
    units: str,
):
    """
    Executes fieldline_trace using the model already loaded in memory.
    If Fortran calls ERROR STOP, only this worker process terminates.
    """
    x, s, bounded = fieldline_trace(
        x0=pt,
        idir=direction,
        ds=ds,
        nsteps=nsteps,
        stop_at_boundary=stop_at_boundary,
        coordinates=coord_sys,
        angular_units=units,
    )
    return np.asarray(x), np.asarray(s), bool(bounded)


class MagneticModel:
    """
    Encapsulates an HSX magnetic configuration loaded through FLARE/EMC3-EIRENE.
    """

    def __init__(self, model_name: str, model_path: Union[str, Path]):
        self.model_name = model_name
        self.path = str(model_path)
        self.__model_loaded = False

    def __enter__(self):
        self.load_model()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__model_loaded:
            self.remove_model()

    def is_loaded(self) -> bool:
        return self.__model_loaded

    def load_model(self) -> None:
        try:
            model.load(self.path)
        except Exception as e:
            raise RuntimeError(f"Failed to load FLARE model '{self.path}': {e}")
        else:
            self.__model_loaded = True

    def remove_model(self) -> None:
        if not self.__model_loaded:
            raise RuntimeError("Cannot remove model: no magnetic model is currently loaded.")
        model.free()
        self.__model_loaded = False

    def calculate_bfield(
        self, point: Union[Tuple[float, float, float], np.ndarray]
    ) -> np.ndarray:
        """Evaluates magnetic field vector B = [Bx, By, Bz] (in Tesla)."""
        if not self.__model_loaded:
            raise RuntimeError("Model must be loaded via load_model() before evaluating B-field.")

        pt = np.asarray(point, dtype=float).flatten()
        b_vec = bfield.eval(float(pt[0]), float(pt[1]), float(pt[2]))
        return np.asarray(b_vec, dtype=float)

    def calculate_fieldline(
        self,
        initial_position: Union[Tuple[float, float, float], np.ndarray],
        direction: int = 1,
        step_size: float = 0.01,
        num_steps: int = 1000,
        beyond_boundary: bool = False,
        coordinate_system: str = "cartesian",
        angular_coord_units: str = "rad",
        safe: bool = True,
        timeout_sec: float = 15.0,
    ) -> Tuple[bool, Optional[np.ndarray], Optional[np.ndarray], bool]:
        """
        Traces a magnetic fieldline through the loaded configuration.
        If safe=True, uses util.process.run_isolated to prevent Fortran crashes.
        """
        if not self.__model_loaded:
            raise RuntimeError("Model must be loaded via load_model() before tracing.")

        pt = [float(v) for v in np.asarray(initial_position).flatten()]
        stop_at_boundary = not beyond_boundary

        if safe:
            success, result, err = run_isolated(
                _trace_worker,
                pt,
                direction,
                step_size,
                num_steps,
                stop_at_boundary,
                coordinate_system,
                angular_coord_units,
                timeout=timeout_sec,
            )
            if success and result is not None:
                x, s, bounded = result
                return True, x, s, bounded
            return False, None, None, False

        # Direct in-process execution
        try:
            x, s, bounded = fieldline_trace(
                x0=pt,
                idir=direction,
                ds=step_size,
                nsteps=num_steps,
                stop_at_boundary=stop_at_boundary,
                coordinates=coordinate_system,
                angular_units=angular_coord_units,
            )
            return True, np.asarray(x), np.asarray(s), bool(bounded)
        except Exception:
            return False, None, None, False