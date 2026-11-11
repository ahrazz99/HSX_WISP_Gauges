"""
scripts/test_pipeline.py
Verification test script for the WISP package.
"""

from pathlib import Path
import sys
import json
import numpy as np

# Automatically add 'src/' to Python path so it works without needing pip install
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from util.geometry import (
    cartesian_to_cylindrical,
    cylindrical_to_cartesian,
    angular_vector_separation,
    get_hsx_octant_transform,
    HSX_OCTANTS,
)
from magnetic_analysis.port import Port
from magnetic_analysis.port_manager import PortManager
from magnetic_analysis.physical_model import PhysicalModel


def print_status(test_name: str, passed: bool, detail: str = ""):
    status = "\033[92m[PASS]\033[0m" if passed else "\033[91m[FAIL]\033[0m"
    print(f"{status} {test_name}" + (f": {detail}" if detail else ""))


# =============================================================================
# Test 1: Geometry and Coordinate Conversions
# =============================================================================
def test_geometry():
    print("\n--- Test 1: Geometry & Coordinate Math ---")
    
    # 1. Round-trip Cylindrical <-> Cartesian
    x, y, z = 1.370, 0.065, 0.342
    r, z_cyl, phi = cartesian_to_cylindrical(x, y, z, degrees=True)
    x_rec, y_rec, z_rec = cylindrical_to_cartesian(r, z_cyl, phi, degrees=True)
    
    coord_match = np.allclose([x, y, z], [x_rec, y_rec, z_rec], atol=1e-5)
    print_status("Cylindrical <-> Cartesian round-trip", coord_match)

    # 2. Angular vector separation
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    sep_90 = np.isclose(angular_vector_separation(v1, v2), 90.0)
    print_status("Vector angular separation (90 deg)", sep_90)

    # 3. Octant transforms
    mat_a = get_hsx_octant_transform("A")
    is_identity = np.allclose(mat_a, np.eye(3))
    print_status("Octant A transform is Identity matrix", is_identity)


# =============================================================================
# Test 2: PortManager Generation & Ground-Truth Verification
# =============================================================================
def test_port_manager():
    print("\n--- Test 2: PortManager & Symmetry Expansion ---")

    json_path = PROJECT_ROOT / "data" / "hsx_octant_ports.json"
    if not json_path.exists():
        print_status("Port JSON exists", False, f"Missing {json_path}")
        return

    # 1. Load and expand symmetry
    manager = PortManager.from_json(json_path)
    all_ports = manager.list_ports()
    
    # 13 base ports * 8 octants = 104 ports total
    count_ok = len(all_ports) == 104
    print_status("104 machine-wide ports generated across 8 octants", count_ok, f"Count = {len(all_ports)}")

    # 2. Verify calculated coordinates against historical data (data/max_port_positions.json)
    ground_truth_path = PROJECT_ROOT / "data" / "max_port_positions.json"
    if ground_truth_path.exists():
        with open(ground_truth_path, "r") as f:
            ground_truth = json.load(f)

        max_err = 0.0
        compared = 0
        for octant_sec, positions in ground_truth.items():
            for pos_name, expected_coord in positions.items():
                port_name = f"{octant_sec}{pos_name}"
                if port_name in manager.ports:
                    calc_coord = manager.get_port(port_name).position
                    err = np.linalg.norm(calc_coord - np.array(expected_coord))
                    max_err = max(max_err, err)
                    compared += 1

        matches_truth = max_err < 1e-4
        print_status(
            f"Coordinate verification against ground truth ({compared} ports)",
            matches_truth,
            f"Max deviation = {max_err:.6e} m"
        )

    # 3. Test Occupancy CRUD
    test_port = "A12TT"
    print_status("Port initially unoccupied", not manager.is_port_occupied(test_port))
    
    manager.occupy_port(test_port, occupant="WISP_GAUGE_01")
    print_status("Port occupied successfully", manager.is_port_occupied(test_port))
    
    gauge = manager.deoccupy_port(test_port)
    print_status("Port deoccupied successfully", (not manager.is_port_occupied(test_port)) and gauge == "WISP_GAUGE_01")


# =============================================================================
# Test 3: PhysicalModel & STL Mesh Flood-Fill
# =============================================================================
def test_physical_model():
    print("\n--- Test 3: PhysicalModel Mesh & Flood-Fill ---")

    stl_path = PROJECT_ROOT / "data" / "HSX_ASSEMBLY_RECONSTRUCTED.STL"
    if not stl_path.exists():
        print_status("STL Mesh exists", False, f"Missing {stl_path}")
        return

    print("Loading 47MB STL mesh (this may take a few seconds)...")
    try:
        model = PhysicalModel(stl_path=stl_path)
        print_status("STL Mesh loaded and cell normals computed", model.mesh is not None)
    except Exception as e:
        print_status("STL Mesh loaded", False, str(e))
        return

    # Test flood-fill port detection near port A12TT
    approx_a12tt = np.array([1.3701, 0.0646, 0.3423])
    try:
        centroid, inward_normal, region = model.find_port_surface(approx_a12tt, angle_tolerance_deg=5.0)
        norm_len = np.linalg.norm(inward_normal)
        dist_to_seed = np.linalg.norm(centroid - approx_a12tt)

        print_status(
            "Port surface flood-fill extracted",
            np.isclose(norm_len, 1.0) and dist_to_seed < 0.05,
            f"Detected centroid: [{centroid[0]:.3f}, {centroid[1]:.3f}, {centroid[2]:.3f}], Inward normal: [{inward_normal[0]:.3f}, {inward_normal[1]:.3f}, {inward_normal[2]:.3f}]"
        )
    except Exception as e:
        print_status("Port surface flood-fill extracted", False, str(e))


# =============================================================================
# Test 4: FLARE / EMC3 Environment Check
# =============================================================================
def test_flare():
    print("\n--- Test 4: External FLARE / EMC3 Environment ---")
    try:
        from flare import model
        from flare.analysis import bfield
        print_status("FLARE module importable", True)
    except ImportError:
        print_status("FLARE module importable", False, "FLARE / EMC3 libraries not found in this Python environment (expected if running outside the dedicated WSL container).")


if __name__ == "__main__":
    print("==================================================")
    print("        RUNNING HSX WISP PIPELINE TESTS           ")
    print("==================================================")
    test_geometry()
    test_port_manager()
    test_physical_model()
    test_flare()
    print("\n==================================================")
    print("                  TESTS COMPLETE                  ")
    print("==================================================")