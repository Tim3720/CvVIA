# 📊 CvVIA app

A flexible visualization tool for **images and videos** with a powerful **script-based processing system**.

Define your own processing logic using simple Python scripts — similar to an Arduino-style workflow — and visualize results in real time.

---

## ✨ Features

* 🎥 Load and visualize **videos and image sequences**
* 🧠 **Custom processing scripts** (plug-and-play)
* 🔍 Automatic **ROI (Region of Interest) handling**
* 📈 Integrated **Matplotlib visualization**
* 💾 Export processed data easily
* 🧩 Modular design for easy extension

---

## 🧠 Concept

Instead of hardcoding functionality, this app lets you define your own processing pipeline via a Python script.

The app handles:

* File loading
* Frame iteration
* ROI extraction
* UI & visualization

You focus only on:
👉 **How the data is processed**

---

## 🔄 Processing Lifecycle

Your script follows this structure:

```python
setup()

for each frame:
    processed = process_frame(...)
    for each ROI:
        process_roi(...)

save_data()
```

---

## 📜 Script API

Each script must implement the following functions:

### `setup(fig)`

Called once at startup.

Use it to:

* Initialize plots
* Reset global state

---

### `process_frame(frame, idx, fig) -> np.ndarray`

Called once per frame.

* Input: raw frame
* Output: processed frame (used for ROI detection)

---

### `process_roi(roi, roi_org, roi_processed, roi_idx, idx, fig) -> np.ndarray`

Called for each ROI.

* `roi`: ROI from processed frame
* `roi_org`: original ROI
* `roi_processed`: processed ROI
* Returns: visualization image (displayed in UI)

👉 This is where most of your logic goes.

---

### `save_data(fig, save_path)`

Called after processing finishes.

Use it to:

* Save results
* Export files
* Store computed data

---

## 🧪 Example Script

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

## 📦 Installation

### Using pip

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
python main.py --input <path_to_video_or_images> --script <script.py>
```

Example:

```bash
python main.py --input data/video.mp4 --script scripts/my_script.py
```

---

## 🧩 Dependencies

Core dependencies include:

* `numpy`
* `opencv-python`
* `PySide6`
* `matplotlib`
* `scipy`

(See `requirements.txt` for full list)

---

## 🛠️ Development

Clone the repository:

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

Create environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📁 Project Structure

```id="p3d2w1"
.
├── main.py
├── scripts/          # User scripts
├── core/             # Core processing logic
├── ui/               # GUI components
├── utils/            # Helper functions
└── requirements.txt
```

---

## 🎯 Design Goals

* 🧩 **Modularity** — plug in new functionality via scripts
* ⚡ **Fast iteration** — no recompiling, just edit & run
* 🧠 **User control** — full flexibility in processing
* 🖥️ **Visualization-first** workflow

---

## 🚀 Future Ideas

* Live script reloading 🔄
* Script marketplace / sharing 📦
* 3D visualization improvements 🌐
* GPU acceleration ⚡

---

## 🤝 Contributing

Contributions are welcome!

* Fork the repo
* Create a feature branch
* Submit a PR

---

## 📄 License

MIT License (or your preferred license)

---

## 💡 Inspiration

This project follows a philosophy similar to:

* Arduino sketches (setup + loop)
* Shader programming pipelines
* Scientific scripting workflows



## 📄 License

This project is licensed under the MIT License – see the LICENSE file for details.
