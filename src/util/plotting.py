"""
src/util/plotting.py
Matplotlib routines for 2D cross sections, model comparison charts,
and 3D fieldline trajectories.
"""

from pathlib import Path
from typing import List, Optional, Union, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np


def plot_model_comparison(
    port_names: List[str],
    angular_separations: List[float],
    threshold_deg: float = 10.0,
    title: str = "Magnetic Field Vector Separation Across HSX Ports",
    save_path: Optional[Union[str, Path]] = None,
) -> plt.Figure:
    """
    Creates a bar chart showing the angular separation (in degrees) between two
    magnetic models at the WISP probe tip for each port.

    Ports exceeding threshold_deg are highlighted in red.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    bars = ax.bar(
        port_names, angular_separations, color="royalblue", edgecolor="black", width=0.6
    )

    # Highlight any port that exceeds the threshold criteria
    for bar, angle in zip(bars, angular_separations):
        if angle > threshold_deg:
            bar.set_color("crimson")
            bar.set_edgecolor("darkred")

    ax.axhline(
        threshold_deg,
        color="red",
        linestyle="--",
        linewidth=1.8,
        label=f"Acceptance Limit ({threshold_deg}°)",
    )

    ax.set_xlabel("HSX Port Identifier", fontsize=11, fontweight="bold")
    ax.set_ylabel("Field Vector Separation (degrees)", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xticks(range(len(port_names)))
    ax.set_xticklabels(port_names, rotation=60, ha="right", fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300)

    return fig


def plot_fieldlines_3d(
    fieldlines: List[np.ndarray],
    port_centroids: Optional[Dict[str, np.ndarray]] = None,
    title: str = "Traced Fieldlines and Port Locations",
    save_path: Optional[Union[str, Path]] = None,
) -> plt.Figure:
    """
    Plots traced 3D fieldlines and optional labeled port centroids using Matplotlib.

    Args:
        fieldlines: List of (3, N) or (N, 3) arrays of Cartesian fieldline coordinates.
        port_centroids: Optional dict mapping port name to [x, y, z] centroid array.
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(projection="3d")

    # Plot fieldlines
    for idx, fl in enumerate(fieldlines):
        pts = np.asarray(fl)
        if pts.shape[0] == 3 and pts.shape[1] != 3:
            pts = pts.T
        ax.plot(
            pts[:, 0], pts[:, 1], pts[:, 2], label=f"Line {idx+1}" if idx < 5 else None
        )

    # Plot port markers
    if port_centroids:
        for name, coord in port_centroids.items():
            ax.scatter(coord[0], coord[1], coord[2], color="red", s=30)
            ax.text(coord[0], coord[1], coord[2], f" {name}", fontsize=8, color="blue")

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.set_title(title, fontweight="bold")
    if len(fieldlines) <= 5:
        ax.legend()

    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300)

    return fig


def plot_poincare_surface(
    r_coords: np.ndarray,
    z_coords: np.ndarray,
    title: str = "Poincaré Poloidal Section",
    save_path: Optional[Union[str, Path]] = None,
) -> plt.Figure:
    """
    Plots a 2D (R, Z) Poincaré puncture plot of fieldlines.
    """
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(r_coords, z_coords, s=1, color="navy", alpha=0.6)

    ax.set_xlabel("R (m)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Z (m)", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_aspect("equal")
    ax.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300)

    return fig