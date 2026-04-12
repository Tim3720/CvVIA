"""
Template script for the CvVIA app.

Users must implement the following functions:

    - setup(fig)
    - process_frame(frame, idx, fig)
    - process_roi(roi, roi_org, roi_processed, roi_idx, idx, fig)
    - save_data(fig, save_path)


The setup function and process functions are called automatically, while the save_data
function is only called when the user presses the according button in the app.

Typical lifecycle:

    setup()

    for each frame:
        processed = process_frame(...)
        for each ROI:
            process_roi(...)

    save_data()
"""

import os
import numpy as np
from matplotlib.figure import Figure


# ---------------------------------------------------------------------
# GLOBAL STATE (optional)
# ---------------------------------------------------------------------
# Use global variables to persist data across frames

results = {}
axs = []


# ---------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------
def setup(fig: Figure):
    """
    Called once before processing starts.

    Use this to:
    - Initialize plots
    - Reset global variables
    - Configure visualization
    """

    results.clear()
    axs.clear()

    # Example: create a plot (optional)
    ax = fig.add_subplot(1, 1, 1)
    axs.append(ax)


# ---------------------------------------------------------------------
# FRAME PROCESSING
# ---------------------------------------------------------------------
def process_frame(frame: np.ndarray, idx: int, fig: Figure) -> np.ndarray:
    """
    Called once per frame.

    Parameters
    ----------
    frame : np.ndarray
        Input frame (format depends on the app, typically grayscale or BGR).
    idx : int
        Frame index.
    fig : Figure
        Matplotlib figure for optional visualization.

    Returns
    -------
    np.ndarray
        Processed frame (used for ROI extraction).
    """

    # --- USER CODE START ---
    processed = frame  # replace with your processing
    # --- USER CODE END ---

    return processed


# ---------------------------------------------------------------------
# ROI PROCESSING
# ---------------------------------------------------------------------
def process_roi(
    roi: np.ndarray,
    roi_org: np.ndarray,
    roi_processed: np.ndarray,
    roi_idx: int,
    idx: int,
    fig: Figure,
) -> np.ndarray:
    """
    Called for each ROI in each frame.

    Parameters
    ----------
    roi : np.ndarray
        ROI rectangle.
    roi_org : np.ndarray
        ROI crop of original frame.
    roi_processed : np.ndarray
        ROI crop of processed frame.
    roi_idx : int
        ROI index within the frame.
    idx : int
        Frame index.
    fig : Figure
        Matplotlib figure.

    Returns
    -------
    np.ndarray
        Visualization image (must match ROI size, usually BGR or grayscale).
    """

    # --- USER CODE START ---

    # Example placeholder logic
    output = roi_org.copy()

    # Store something (example)
    if idx not in results:
        results[idx] = []

    results[idx].append({
        "roi_idx": roi_idx,
        "mean_intensity": float(np.mean(roi_org))
    })

    # Optional: draw on output
    # e.g. cv2.rectangle(...)

    # --- USER CODE END ---

    return output


# ---------------------------------------------------------------------
# SAVE DATA
# ---------------------------------------------------------------------
def save_data(fig: Figure, save_path: str):
    """
    Called when user requests it.

    Use this to:
    - Save computed data
    - Export plots
    - Write files

    Parameters
    ----------
    fig : Figure
        Matplotlib figure used during processing.
    save_path : str
        Directory where output files should be written.
    """

    os.makedirs(save_path, exist_ok=True)

    # --- USER CODE START ---

    output_file = os.path.join(save_path, "results.txt")

    with open(output_file, "w") as f:
        for frame_idx, entries in results.items():
            for entry in entries:
                f.write(f"{frame_idx},{entry['roi_idx']},{entry['mean_intensity']}\n")

    # Optional: save figure
    fig.savefig(os.path.join(save_path, "figure.png"))

    # --- USER CODE END ---
