"""
Example processing script for the CvVIA app.

This script demonstrates how to detect cuts made by a laser or scalpel within
a sample using X-ray image data. The input consists of scans captured at
different heights, forming a stack of cross-sectional images.

ROI REQUIREMENTS
----------------
For the algorithm to work correctly, the user must manually define a Region of
Interest (ROI) around the surface where the cut is located.

Important:
    - The ROI must include part of the sample
    - The ROI must include part of the background

This contrast is required for reliable surface detection.

EXECUTION FLOW
--------------
The following functions are called automatically by the application:
    - setup
    - process_frame
    - process_roi

The save_data function is only executed when triggered explicitly by the user
via the application UI.

FUNCTION OVERVIEW
----------------

setup(fig):
    Initializes the script by clearing global data structures and resetting
    the plotting axes.

process_frame(frame, idx, fig):
    Processes the full frame by converting it into a binary image using
    automatic thresholding (cv2.THRESH_OTSU). This is a preview of how the binary is
    created for each ROI

process_roi(roi, roi_org, roi_processed, roi_idx, idx, roi_keys, fig):
    Contains the main processing logic applied to each ROI:

    1. Thresholding:
        - Converts the ROI into a binary image using cv2.THRESH_OTSU

    2. Contour Detection:
        - Extracts contours from the binary image
        - Filters out small contours based on area

    3. Contour Classification:
        - Identifies the largest contour (assumed to be the sample surface)
        - Classifies contours inside it as inner contours (e.g., holes)

    4. Surface Estimation:
        - Creates a mask of the largest contour and its inverse
        - Applies dilation to both masks
        - Computes the surface region via a bitwise AND operation

    5. Post-processing:
        - Extracts surface points (used as a 3D point cloud across frames)
        - Stores contours and points
        - Updates visualization

save_data(fig, save_path):
    Saves the computed results into three files:

    - point_cloud.dat:
        3D surface points across frames (cuts included as part of the surface)

    - surface_contours.dat:
        Outer contour of the detected surface (closed loop)

    - inner_contours.dat:
        Inner contours within the sample (e.g., holes or cuts)


The ROI visualization then shows the estimated surface in cyan and the inner contours in
yellow.

SUMMARY
-------
This script demonstrates how to extract geometric features from volumetric
image data, track them across frames, and reconstruct surface information
as a point cloud.
"""

import os
import numpy as np
from matplotlib.figure import Figure

# other dependencies:
import cv2


# ---------------------------------------------------------------------
# GLOBAL STATE (optional)
# ---------------------------------------------------------------------
# Use global variables to persist data across frames

axs = []
contours = {}
inner_contours = {}
point_clouds = {}


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

    axs.clear()
    contours.clear()
    point_clouds.clear()
    inner_contours.clear()
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    axs.append(ax)

    print("Setup finished, cleared data and plot")


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

    thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_OTSU)[1]

    return thresh


# ---------------------------------------------------------------------
# ROI PROCESSING
# ---------------------------------------------------------------------
def process_roi(
    roi: np.ndarray,
    roi_org: np.ndarray,
    roi_processed: np.ndarray,
    roi_idx: int,
    idx: int,
    roi_keys: list,
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

    # for result visualization:
    res = cv2.cvtColor(roi_org, cv2.COLOR_GRAY2BGR)

    # image to binary image:
    thresh = cv2.threshold(roi_org, 0, 255, cv2.THRESH_OTSU)[1]

    # find all contours within the binary image:
    cnts, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

    # filter out very small parts:
    cutoff_area = 20
    filtered_indices = [
        i for i in range(len(cnts)) if cv2.contourArea(cnts[i]) > cutoff_area
    ]
    hierarchy = hierarchy[0][filtered_indices]
    cnts = [cnts[i] for i in filtered_indices]
    cnt_areas = [cv2.contourArea(cnt) for cnt in cnts]

    # find largest contour:
    largest_cnt_idx = int(np.argmax(cnt_areas))
    largest_cnt = cnts[largest_cnt_idx]

    inner_cnts = []
    for i, h in enumerate(hierarchy):
        if h[3] == largest_cnt_idx:
            inner_cnts.append(cnts[i])


    cv2.drawContours(res, [largest_cnt], -1, (0, 255, 0), 1)
    cv2.drawContours(res, inner_cnts, -1, (0, 255, 255), 1)

    mask = np.zeros_like(roi_org)
    cv2.drawContours(mask, [largest_cnt], -1, (255,), -1)

    mask_inv = cv2.bitwise_not(mask)

    kernel = np.ones((3, 3)) / 9
    mask = cv2.dilate(mask, kernel)
    mask_inv = cv2.dilate(mask_inv, kernel)

    surface = cv2.bitwise_and(mask, mask_inv)

    filtered_cnts = list(
        cv2.findContours(surface, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    )
    filtered_cnts.sort(key=lambda x: cv2.arcLength(x, True), reverse=True)
    filtered_cnt = filtered_cnts[0].reshape(-1, 2)

    mask *= 0
    cv2.drawContours(mask, [filtered_cnt], -1, (255,), 3)

    surface = cv2.bitwise_and(surface, mask)
    res[:, :, 0] += surface

    pts = cv2.findNonZero(surface)
    pts = pts.reshape(-1, 2)

    point_clouds[idx] = pts
    contours[idx] = filtered_cnt
    inner_contours[idx] = inner_cnts

    # Optional plotting of surface (slows down the processing but usefull for debugging):
    # axs[0].plot(
    #     filtered_cnt[:, 0], filtered_cnt[:, 1], np.ones(len(filtered_cnt)) * idx
    # )

    return res


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

    with open(os.path.join(save_path, "point_cloud.dat"), "w") as f:
        header = "Frame Index: P1x,P1y,P2x,P2y,...\n"
        lines = [header]
        for frame, points in point_clouds.items():
            c = points.flatten()
            line = str(frame) + ":"
            for elem in c:
                line += str(elem) + ","
            line = line[:-1]
            line += "\n"
            lines.append(line)
        f.writelines(lines)

    with open(os.path.join(save_path, "surface_contours.dat"), "w") as f:
        header = "Frame Index: P1x,P1y,P2x,P2y,...\n"
        lines = [header]
        for frame, cnt in contours.items():
            c = cnt.flatten()
            line = str(frame) + ":"
            for elem in c:
                line += str(elem) + ","
            line = line[:-1]
            line += "\n"
            lines.append(line)
        f.writelines(lines)

    with open(os.path.join(save_path, "inner_contours.dat"), "w") as f:
        header = "Frame Index: P1x,P1y,P2x,P2y,...\n"
        lines = [header]
        for frame, cnts in inner_contours.items():
            for cnt in cnts:
                c = cnt.flatten()
                line = str(frame) + ":"
                for elem in c:
                    line += str(elem) + ","
                line = line[:-1]
                line += "\n"
                lines.append(line)
        f.writelines(lines)

    print(f"Successfully saved data for {len(point_clouds)} frames.")
    contours.clear()
    point_clouds.clear()
    inner_contours.clear()
    print("Cleared data")
