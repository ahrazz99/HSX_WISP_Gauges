"""
scripts/compare_models.py
Full analysis workflow testing:
- PortManager loading & probe geometry
- MagneticModel loading, B-field evaluation, and fieldline tracing via FLARE
- Vector separation calculation
- I/O: HDF5 output and manifest.json run tracking
- 2D Plotting: Model comparison bar chart
"""

from pathlib import Path
import sys
import numpy as np

# Ensure src/ is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from magnetic_analysis.port_manager import PortManager
from magnetic_analysis.magnetic_model import MagneticModel
from util.geometry import angular_vector_separation
from util.io import create_run_directory, save_simulation
from util.plotting import plot_model_comparison


def main():
    print("==================================================")
    print("     STARTING FULL HSX FLARE ANALYSIS RUN         ")
    print("==================================================")

    # 1. Initialize Ports
    ports_json = PROJECT_ROOT / "data" / "hsx_octant_ports.json"
    port_manager = PortManager.from_json(ports_json)
    
    # Target ports defined in historical analysis
    eval_ports = [
        "A12TT", "A12MT", "A12MM", "A12MB",
        "A23TT", "A23MT", "A23MM", "A23MB", "A23BB",
        "AP12BB", "AP12MB", "AP12MM", "AP12MT"
    ]
    probe_length = 0.05  # 5 cm standard probe depth

    # Calculate probe tip coordinates (centroid + length * normal)
    tip_coords = {}
    for name in eval_ports:
        port = port_manager.get_port(name)
        tip_coords[name] = port.position + (probe_length * port.normal)

    # 2. Evaluate Model 1 using MagneticModel Class
    print("\n[1/4] Running Model 1: QHS (HSX/qhs/mgrid)...")
    model_qhs = MagneticModel(model_name="qhs", model_path="HSX/qhs/mgrid")
    model_qhs.load_model()

    b_vectors_m1 = {}
    for name in eval_ports:
        b_vec = model_qhs.calculate_bfield(tip_coords[name])
        b_vectors_m1[name] = b_vec

    # Test fieldline tracing feature on MagneticModel
    print("  Testing FLARE fieldline tracing on Model 1...")
    test_seed = tip_coords["A12TT"]
    fl_x, fl_s, bounded = model_qhs.calculate_fieldline_forward(
        initial_position=test_seed,
        direction=1,
        step_size=1.0 / 180.0 * np.pi,
        num_steps=180,
    )
    print(f"  Fieldline traced successfully: {fl_x.shape[1]} points generated (Bounded={bounded})")

    model_qhs.remove_model()

    # 3. Evaluate Model 2 using MagneticModel Class
    print("\n[2/4] Running Model 2: Hill 8 (HSX/hill_8_config)...")
    model_hill = MagneticModel(model_name="hill_8", model_path="HSX/hill_8_config")
    model_hill.load_model()

    b_vectors_m2 = {}
    separations = []

    print("\n--- B-Field Vector Evaluation at Probe Tips ---")
    for name in eval_ports:
        b_vec = model_hill.calculate_bfield(tip_coords[name])
        b_vectors_m2[name] = b_vec

        # Compute angular separation
        sep = angular_vector_separation(b_vectors_m1[name], b_vec, degrees=True)
        separations.append(sep)
        print(f"  Port {name:<7} | B_qhs = {np.linalg.norm(b_vectors_m1[name]):.4f}T, B_hill = {np.linalg.norm(b_vec):.4f}T | Sep: {sep:.3f}°")

    model_hill.remove_model()

    # 4. Save Run Outputs via util.io
    print("\n[3/4] Creating Run Directory and Saving Datasets...")
    output_dir = create_run_directory(
        output_root=PROJECT_ROOT / "output",
        base_model="qhs_vs_hill8",
        configuration_percent="0"
    )

    input_data = {
        "model_1": "HSX/qhs/mgrid",
        "model_2": "HSX/hill_8_config",
        "probe_length_m": probe_length,
        "ports_evaluated": eval_ports,
    }

    output_data = {
        "port_names": np.array(eval_ports, dtype="S"),
        "b_vectors_qhs": np.array([b_vectors_m1[p] for p in eval_ports]),
        "b_vectors_hill": np.array([b_vectors_m2[p] for p in eval_ports]),
        "angular_separations_deg": np.array(separations),
        "sample_fieldline_trace": fl_x,
    }

    save_simulation(
        run_directory=output_dir,
        input_data=input_data,
        output_data=output_data,
        metadata={
            "success": True,
            "max_separation_deg": float(max(separations)),
            "all_under_10_deg": bool(max(separations) < 10.0),
        },
    )
    print(f"  Saved HDF5 data & manifest.json to: {output_dir}")

    # 5. Generate and Save Plot via util.plotting
    print("\n[4/4] Generating 2D Model Comparison Plot...")
    plot_path = output_dir / "plots" / "bfield_separation_comparison.png"
    plot_model_comparison(
        port_names=eval_ports,
        angular_separations=separations,
        threshold_deg=10.0,
        title="HSX B-Field Separation: QHS vs. Hill_8 at WISP Probe Tip (5cm)",
        save_path=plot_path,
    )
    print(f"  Plot successfully saved to: {plot_path}")

    print("\n==================================================")
    print("             FULL RUN COMPLETE (SUCCESS)          ")
    print("==================================================")


if __name__ == "__main__":
    main()