"""
src/magnetic_analysis/physical_model.py
Manages physical geometry for HSX: STL assembly meshes, vacuum wall surfaces,
flood-fill port detection, and ray tracing.
"""

from pathlib import Path
from typing import Tuple, List, Optional, Union
import numpy as np
import pyvista as pv

# Optional import of moose geometry in case environment lacks the C-extension during unit tests
try:
    from moose import geometry as moose_geometry
    HAS_MOOSE = True
except ImportError:
    HAS_MOOSE = False


class PhysicalModel:
    """
    Physical model class that generates an object containing the physical wall and mesh geometry for the HSX vessel
    
    Attributes:
        stl_path: Path object representing the path to the stl file for HSX
        wall_path: Path object representing the path to the wall file for HSX.
        mesh : pyvista polydata representation of the HSX mesh
        wall_surface pyvista polydata representation of the HSX wall surfaces. 
    """

    def __init__(
        self,
        stl_path: Optional[Union[str, Path]] = None,
        wall_path: Optional[Union[str, Path]] = None,
    ):
        """
        constructor for the PhysicalModel object. Pulls in the file paths and loads the stl and wall using the methods if the paths are given.
        
        Args:
            stl_path: Path object representing the path to the stl file for HSX
            wall_path: Path object representing the path to the wall file for HSX.
        
        Returns:
            PhysicalModel object.
        """
        self.stl_path = Path(stl_path) if stl_path else None
        self.wall_path = Path(wall_path) if wall_path else None

        self.mesh: Optional[pv.PolyData] = None
        self.wall_surface: Optional[pv.PolyData] = None

        if self.stl_path:
            self.load_stl(self.stl_path)
        if self.wall_path:
            self.load_wall(self.wall_path)

    def load_stl(self, stl_path: Union[str, Path]) -> pv.PolyData:
        """
        Loads the HSX stl mesh and computes the normals. 
        
        Args:
            stl_path: Path object representing the path to the stl file for HSX
        
        Returns:
            pyvista PolyData containing the mesh
        
        Raises:
            FileNotFoundError if the stl path is invalid.
            Any associated errors with loading a mesh incorrectly into pyvista.
        """
        path = Path(stl_path)
        if not path.is_file():
            raise FileNotFoundError(f"HSX STL file not found: {path}")

        raw_mesh = pv.read(str(path))
        # Compute cell normals to accurately represent flat port faces
        self.mesh = raw_mesh.compute_normals(
            cell_normals=True, point_normals=False, inplace=False
        )
        return self.mesh

    def load_wall(self, wall_path: Union[str, Path]) -> pv.PolyData:
        """
        Loads the toroidal plasma wall boundary using moose.geometry.Torosurf.
        
        Args:
            wall_path: Path object representing the path to the wall file for HSX.
        
        Returns:
            pyvista PolyData object containing the wall
        
        Raises:
            ImportError if Moose is not properly installed.
            FileNotFoundError if the wall file path is invalid
            Any other errors associated with Moose.
        """
        if not HAS_MOOSE:
            raise ImportError("EMC3-EIRENE 'moose' library is required to load Torosurf wall files.")

        path = Path(wall_path)
        if not path.is_file():
            raise FileNotFoundError(f"Wall file not found: {path}")

        wall_grids = moose_geometry.Torosurf.loadtxt(str(path)).grid.vtk()
        wall_pv = pv.wrap(wall_grids[0])
        self.wall_surface = wall_pv.extract_surface()
        return self.wall_surface

    def find_port_surface(
        self,
        seed_point: Union[np.ndarray, Tuple[float, float, float]],
        angle_tolerance_deg: float = 5.0,
    ) -> Tuple[np.ndarray, np.ndarray, pv.PolyData]:
        """
        Identifies a flat port face on the STL mesh using a flood-fill algorithm
        starting from a target coordinate or picked seed cell.

        Args:
            seed_point: Approximate [x, y, z] coordinate near the port opening.
            angle_tolerance_deg: Maximum angular deviation (degrees) between neighboring
                                 cell normals to be considered part of the same flat face.

        Returns:
            region_centroid: Exact [x, y, z] center of the flat face.
            inward_normal: Unit normal vector pointing into the vacuum vessel.
            flat_region_mesh: PyVista PolyData representing the isolated port face.
        """
        if self.mesh is None:
            raise RuntimeError("STL mesh is not loaded. Call load_stl() first.")

        seed_pt = np.asarray(seed_point, dtype=float)
        seed_cell_id = self.mesh.find_closest_cell(seed_pt)
        if seed_cell_id == -1:
            raise ValueError(f"Could not locate a cell near point {seed_point}")

        seed_normal = self.mesh.cell_normals[seed_cell_id]
        cos_tolerance = np.cos(np.radians(angle_tolerance_deg))

        # Flood-fill surface traversal across mesh connectivity
        visited = {seed_cell_id}
        queue = [seed_cell_id]
        flat_cell_ids = []

        while queue:
            current_cell = queue.pop(0)
            flat_cell_ids.append(current_cell)

            neighbors = self.mesh.cell_neighbors(current_cell, connections="edges")
            for neighbor in neighbors:
                if neighbor not in visited:
                    neighbor_normal = self.mesh.cell_normals[neighbor]
                    # Check if neighbor faces the same direction within tolerance
                    if np.dot(seed_normal, neighbor_normal) >= cos_tolerance:
                        visited.add(neighbor)
                        queue.append(neighbor)

        # Extract the isolated flat region
        flat_region_mesh = self.mesh.extract_cells(flat_cell_ids)
        cell_centers = flat_region_mesh.cell_centers().points
        region_centroid = np.mean(cell_centers, axis=0)

        # Get normal at the centroid and invert it to point inward toward the plasma
        closest_id = self.mesh.find_closest_cell(region_centroid)
        raw_normal = self.mesh["Normals"][closest_id]
        inward_normal = -1.0 * (raw_normal / np.linalg.norm(raw_normal))

        return region_centroid, inward_normal, flat_region_mesh

    def ray_trace_to_wall(
        self,
        start_point: Union[np.ndarray, Tuple[float, float, float]],
        direction: Union[np.ndarray, Tuple[float, float, float]],
    ) -> Tuple[np.ndarray, int]:
        """
        Traces a ray from start_point along direction to find where it strikes the STL mesh wall.

        Returns:
            intersection_points: Array of hit points.
            first_face_id: ID of the first face struck.
        """
        if self.mesh is None:
            raise RuntimeError("STL mesh must be loaded to perform ray tracing.")

        start = np.asarray(start_point, dtype=float)
        dir_vec = np.asarray(direction, dtype=float)
        end = start + (dir_vec * 5.0)  # Project ray 5 meters forward

        points, face_ids = self.mesh.ray_trace(start, end)
        if len(points) == 0:
            raise RuntimeError(f"No intersection found along ray from {start_point}")

        return points, face_ids