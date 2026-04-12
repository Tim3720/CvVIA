# CvVIA App

The **OpenCV Visual Image Analysis (CvVIA) app** is a flexible visualization tool for **images and videos** with a **script-based processing system**.

You can define your own processing logic using Python scripts, and the results are visualized in real time without requiring additional visualization code. At the same time, these scripts remain fully usable outside the app, allowing you to integrate them into your own workflows without being tied to the application.

---

## Features

* Load and visualize **videos and image sequences**
* **Custom processing scripts** with automatic reloading on file changes
* Automatic **ROI (Region of Interest) handling**
* Integrated **Matplotlib-based visualization**
* Easy export of processed data
* Modular architecture for straightforward extension

---

## Concept

Instead of hardcoding functionality, the app delegates all processing logic to user-defined Python scripts.

The application is responsible for:

* File loading
* Frame iteration
* ROI extraction
* User interface and visualization
* Automatic script reloading on changes

The user focuses solely on defining **how the data is processed**.

---

## Script API

Each script must implement the following functions:

### `setup(fig)`

Called once at startup.

Typical use cases:

* Initialize plots
* Reset global state

---

### `process_frame(frame, idx, fig) -> np.ndarray`

Called once per frame.

* **Input:** raw frame
* **Output:** processed frame (used for ROI detection)

---

### `process_roi(roi, roi_org, roi_processed, roi_idx, idx, fig) -> np.ndarray`

Called for each ROI.

* `roi`: ROI from the processed frame
* `roi_org`: original ROI
* `roi_processed`: processed ROI
* **Return value:** visualization image (displayed in the UI)

This function typically contains the main processing logic.

---

### `save_data(fig, save_path)`

Called after processing finishes or when triggered by the user.

Typical use cases:

* Save computed results
* Export data to files
* Store intermediate or final outputs

---

## Example Script

A minimal example:

```python
import numpy as np

results = {}

def setup(fig):
    results.clear()

def process_frame(frame, idx, fig):
    return frame

def process_roi(roi, roi_org, roi_processed, roi_idx, idx, fig):
    results.setdefault(idx, []).append(np.mean(roi_org))
    return roi_org

def save_data(fig, save_path):
    with open(f"{save_path}/results.txt", "w") as f:
        for k, v in results.items():
            f.write(f"{k}: {v}\n")
```

---

## Installation

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py --input <path_to_video_or_images> --script <script.py>
```

Example:

```bash
python main.py --input data/video.mp4 --script scripts/my_script.py
```

---

## Dependencies

Core dependencies include:

* `numpy`
* `opencv-python`
* `PySide6`
* `matplotlib`
* `scipy`

See `requirements.txt` for the full list.

---

## Development

Clone the repository:

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Status

This project is currently under active development.  
Some features are not yet implemented, and bugs or incomplete functionality may occur.

---

## Design Goals

* **Modularity**: Extend functionality through independent scripts
* **Fast iteration**: Modify scripts without restarting or recompiling
* **Decoupling**: Processing logic is independent of the application
* **Visualization-first workflow**: Immediate feedback during development

---

## Inspiration

The design of this project is influenced by:

* Arduino-style programming (setup + loop structure)
* Shader-based processing pipelines
* Scientific and research-oriented scripting workflows

---

## License

This project is licensed under the MIT License. See the [`LICENSE`](https://github.com/Tim3720/CvVIA/blob/main/LICENSE) file for details.
