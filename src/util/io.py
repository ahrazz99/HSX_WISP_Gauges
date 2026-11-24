"""
src/util/io.py
I/O routines for run directory creation, HDF5 saving/loading,
JSON file parsing, and simulation audit manifests.
"""

from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
import json
import hashlib
import re
import numpy as np
import h5py

from magnetic_analysis.port import Port

# Standard HSX Magnetic Configurations
KNOWN_CONFIGURATIONS = {
    "qhs": "Quasi-Helically Symmetric",
    "le": "Low Elongation",
    "he": "High Elongation",
    "hill": "Magnetic Hill",
    "well": "Magnetic Well",
    "mirror": "Mirror Mode",
}


def create_run_directory(
    output_root: Union[str, Path],
    base_model: str,
    configuration_percent: Union[str, float, int] = "0",
) -> Path:
    """
    Creates the run directory for outputting simulation data with dated prefixes.
    Immediately writes an initial manifest.json tagged as 'in_progress' to track
    crashed or aborted runs.

    Example output folder:
        output/2026-11-10_qhs_0pct_run001/

    Args:
        output_root: Base output path (e.g. Path("output")).
        base_model: Configuration identifier (e.g., 'qhs', 'le', 'he', 'hill').
        configuration_percent: Auxiliary coil percentage (QHS is 0).

    Returns:
        Path to the created run directory.
    """
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    model_clean = base_model.strip().lower()
    prefix = f"{date.today().isoformat()}_{model_clean}_{configuration_percent}pct_run"
    pattern = re.compile(re.escape(prefix) + r"(\d{3,})$")

    existing_ids = [
        int(match.group(1))
        for path in output_root.iterdir()
        if path.is_dir() and (match := pattern.fullmatch(path.name))
    ]

    next_id = max(existing_ids, default=0) + 1
    run_directory = output_root / f"{prefix}{next_id:03d}"

    run_directory.mkdir(parents=True, exist_ok=True)
    (run_directory / "data").mkdir(exist_ok=True)
    (run_directory / "plots").mkdir(exist_ok=True)

    # Write initial manifest to track run progress
    initial_manifest = {
        "metadata": {
            "run_id": run_directory.name,
            "status": "in_progress",
            "date": date.today().isoformat(),
            "time_started": datetime.now().time().isoformat(),
            "base_model": base_model,
            "configuration_percent": str(configuration_percent),
        }
    }
    with open(run_directory / "manifest.json", "w") as f:
        json.dump(initial_manifest, f, indent=4)

    return run_directory


def save_data_h5py(run_directory: Path, data: dict, file_name: str) -> Path:
    """
    Saves numerical arrays/dictionaries in HDF5 format inside run_directory/data/.
    """
    run_directory = Path(run_directory)
    data_path = run_directory / "data"
    data_path.mkdir(parents=True, exist_ok=True)

    if not data:
        raise ValueError("The provided data dictionary is empty.")

    if not file_name.endswith(".h5"):
        file_name += ".h5"

    data_file_path = data_path / file_name

    with h5py.File(data_file_path, "w") as h5file:
        for name, values in data.items():
            array = np.asarray(values)
            options = {"compression": "gzip"} if array.ndim > 0 else {}
            h5file.create_dataset(name, data=array, **options)

    return data_file_path


def save_simulation(
    run_directory: Path,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    h5_filename: str = "simulation_data.h5",
) -> Path:
    """
    Saves simulation numerical arrays to HDF5 and updates the manifest.json
    status to 'completed'.
    """
    run_dir = Path(run_directory)
    if metadata is None:
        metadata = {}

    # 1. Save numerical datasets into HDF5
    h5_path = save_data_h5py(run_dir, output_data, h5_filename)

    # 2. Read existing manifest to preserve start time
    manifest_path = run_dir / "manifest.json"
    time_started = None
    if manifest_path.exists():
        try:
            with open(manifest_path, "r") as f:
                old_m = json.load(f)
                time_started = old_m.get("metadata", {}).get("time_started")
        except Exception:
            pass

    # 3. Compute configuration hash
    input_str = json.dumps(input_data, sort_keys=True, default=str)
    config_hash = hashlib.sha256(input_str.encode("utf-8")).hexdigest()[:16]

    manifest = {
        "metadata": {
            "run_id": run_dir.name,
            "status": "completed",
            "format_version": "1.0.0",
            "config_hash": config_hash,
            "date": date.today().isoformat(),
            "time_started": time_started,
            "time_concluded": datetime.now().time().isoformat(),
            "simulation_success": metadata.get("success", True),
            **metadata,
        },
        "input_data": input_data,
        "output_data": {
            "h5_file": str(h5_path.name),
            "saved_datasets": list(output_data.keys()),
        },
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)

    return h5_path


def load_simulation(run_directory: Union[str, Path]) -> Tuple[Dict[str, Any], Dict[str, np.ndarray]]:
    """
    Loads a completed simulation run from its run directory.

    Args:
        run_directory: Path to the run folder (e.g. output/2026-11-10_qhs_0pct_run001).

    Returns:
        (manifest_dict, datasets_dict) where datasets_dict maps dataset names
        to loaded NumPy arrays.
    """
    run_dir = Path(run_directory)
    manifest_path = run_dir / "manifest.json"

    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest.json not found in {run_dir}")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    h5_name = manifest.get("output_data", {}).get("h5_file", "simulation_data.h5")
    h5_path = run_dir / "data" / h5_name

    if not h5_path.is_file():
        raise FileNotFoundError(f"HDF5 data file not found at {h5_path}")

    datasets: Dict[str, np.ndarray] = {}
    with h5py.File(h5_path, "r") as h5file:
        for key in h5file.keys():
            datasets[key] = np.array(h5file[key])

    return manifest, datasets


def load_base_octant_ports(json_path: Path) -> Dict[str, Port]:
    """
    Parses a base octant JSON file into a dictionary of base Port objects.
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