"""
src/util/io.py
I/O routines for run directory creation, HDF5 saving, and JSON file parsing.
"""

from datetime import date
from pathlib import Path
from typing import Dict
import json
import numpy as np
import re
import h5py

from magnetic_analysis.port import Port

def create_run_directory(output_root: Path, base_model: str, configuration_percent: str="0") -> Path:
    """
    Creates the run directory for outputing data for a simulation. If multiple simulations are done on a given day.

    Example: 
        for the first simulation run with qhs on 10/9/2026, the output folder would be:
            2026-10-9_qhs_0pct_run001
        for the 4th simulation of the same parameters on the same day:
            2026-10-9_whs_0pct_run004
        For a 3rd simulation with a different base model and configuration percent:
            2026-10-9_well_8pct_run001
    Args:
        output_root: Python's built-in Path object representing the base dictionary for outputs
        base_model: The base HSX magnetic configuration
        configuration_percent: the base percent for a given configuration - QHS is always 0. 
    
    Returns:
        run_directory_path: python Path object representing the path to the directory created for a given simulations parameters.
        
    """

    #Check that the output root directory exists. If not, make it.
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    #Set up prefixes. For example formats, see function header
    prefix = f"{date.today().isoformat()}_{base_model}_{configuration_percent}_"
    pattern = re.compile(re.escape(prefix) + r"(\d{3,})$")

    #Pull the existing names of directories with the same pattern in the output folder
    existing_ids = [int(match.group(1)) for path in output_root.iterdir() if path.is_dir() if (match := pattern.fullmatch(path.name))]

    #Determine the next id needed for the next simulation
    next_id = max(existing_ids, default=0) + 1
    run_directory = output_root / f"{prefix}{next_id:03d}"

    #Create the run directory and its subdirectories
    run_directory.mkdir()
    (run_directory / "data").mkdir()
    (run_directory / "plots").mkdir()

    return run_directory

def save_data_h5py(run_directory: Path, data: dict, file_name: str) -> Path:
    """
    Saves the given numerical data in an h5 format.
    
    Args:
        run_directory: Path object representing the path to the parent folder for the data.
        data: dict of data to be saved
        file_name: string representation of the desired name for the file 
    
    Returns:
        The path to the stored data as a Path object.

    Raises:
        ValueError: If the directory structure, filename, or data is invalid.
        FileExistsError: If the output file already exists.
    """

    #Checking run directory existence and correctly given as a directory
    if not (run_directory.exists() and run_directory.is_dir()):
        raise ValueError(f"{run_directory} is not a path to a directory for data storage.")

    #Checking that the data directory exists in the parent
    data_path = run_directory / "data"
    if not (data_path.exists() and data_path.is_dir()):
        raise ValueError(f"data directory does not exist in {run_directory}.")

    #Checking that the data dictionary is not empty
    if not data:
        raise ValueError(f"the provided dictionary is empty!")

    #Confirm correct file name given for saving.
    if (not file_name.strip() or "/" in file_name or "\\" in file_name or file_name in {".", ".."}):
        raise ValueError("file_name must be a valid filename.")

    if not file_name.endswith(".h5"):
        file_name += ".h5"

    data_file_path = data_path / file_name

    #Save the data.
    with h5py.File(data_file_path, "x") as h5file:
        for name, values in data.items():
            array = np.asarray(values)

            # Compression is not supported for scalar datasets.
            options = (
                {"compression": "gzip"}
                if array.ndim > 0
                else {}
            )

            h5file.create_dataset(
                name,
                data=array,
                **options,
            )
    return data_file_path
    
def save_simulation(
    run_directory: Path,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    h5_filename: str = "simulation_data.h5",
) -> Path:
    """
    Saves simulation numerical arrays to HDF5 and writes the manifest.json
    audit file to the run directory as specified in the project README.

    Args:
        run_directory: Path to the run directory.
        input_data: Dictionary of input parameters (model, config %, ports evaluated, etc.).
        output_data: Dictionary of output numerical datasets (B-fields, coordinates, angles).
        metadata: Optional dictionary with run metadata (timers, status).
        h5_filename: Name of the HDF5 output file.

    Returns:
        Path to the saved HDF5 file.
    """
    run_dir = Path(run_directory)
    if metadata is None:
        metadata = {}

    # 1. Save numerical datasets into HDF5
    h5_path = save_data_h5py(run_dir, output_data, h5_filename)

    # 2. Compute a hash of the input configuration for traceability
    input_str = json.dumps(input_data, sort_keys=True, default=str)
    config_hash = hashlib.sha256(input_str.encode("utf-8")).hexdigest()[:16]

    # 3. Assemble manifest according to README specifications
    manifest = {
        "metadata": {
            "run_id": run_dir.name,
            "format_version": "1.0.0",
            "config_hash": config_hash,
            "date": date.today().isoformat(),
            "time_recorded": datetime.now().time().isoformat(),
            "simulation_success": metadata.get("success", True),
            **metadata,
        },
        "input_data": input_data,
        "output_data": {
            "h5_file": str(h5_path.name),
            "saved_datasets": list(output_data.keys()),
            "status": "completed",
        },
    }

    manifest_path = run_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)

    return h5_path

def load_base_octant_ports(json_path: Path) -> Dict[str, Port]:
    """
    Parses a base octant JSON file (like `hsx_octant_ports.json`) into
    a dictionary of base Port objects (names keyed by e.g. '12_TT').
    """
    path = Path(json_path)
    if not path.is_file():
        raise FileNotFoundError(f"Port definition file not found: {path}")

    with open(path, "r") as f:
        data = json.load(f)

    base_ports: Dict[str, Port] = {}
    for port_id, info in data.items():
        radius = info.get("dimensions", {}).get("radius", 0.038)
        base_ports[port_id] = Port(
            name=port_id,
            position=np.array(info["position"]),
            normal=np.array(info["normal"]),
            shape=info.get("shape", "circular"),
            diameter=radius * 2.0,
        )

    return base_ports
