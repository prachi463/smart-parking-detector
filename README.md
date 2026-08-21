\# 🚗 Smart Parking Detector



<div align="center">



\[!\[Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

\[!\[OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green.svg)](https://opencv.org/)

\[!\[YOLOv8](https://img.shields.io/badge/YOLOv8-Latest-orange.svg)](https://github.com/ultralytics/ultralytics)

\[!\[Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red.svg)](https://streamlit.io/)

\[!\[License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)



\*\*An intelligent parking space occupancy detection system, combining classical computer vision and YOLOv8 deep learning — available both as a desktop application and a browser-based web app.\*\*



\[Live Web App](#-live-demo) •

\[Features](#-features) •

\[Quick Start](#-quick-start) •

\[How It Works](#-how-it-works) •

\[Project Architecture](#-project-architecture)



</div>



\---



\## 🎓 About This Project



This is a final-year B.Tech (CSE – AI/ML) project by \*\*Prachi Verma\*\*, built on top of the open-source

\[Car-Parking-Detection](https://github.com/8harath/Car-Parking-Detection) project originally created by

\*\*Bharath K\*\* (Jain Deemed to be University) for the PNT Lab selection process at IIT Tirupati Navishkar.



\*\*What I added on top of the original project:\*\*

\- 🌐 A full \*\*Streamlit web interface\*\* (`app\_streamlit.py`) — upload an image, draw parking spaces

&#x20; directly in the browser (no more clunky desktop mouse-drag setup), and get instant results

\- 🔀 A \*\*hybrid detection pipeline\*\* for the web app: YOLOv8 for direct vehicle detection, combined

&#x20; with a classical pixel-density fallback — since pretrained COCO-based models like YOLOv8n are

&#x20; trained almost entirely on street-level photos and struggle to recognize vehicles from a straight-down

&#x20; aerial camera angle

\- 🐛 Fixed a bug in `run.py` where `--mode both` silently skipped video processing entirely

&#x20; (`if mode == "video"` → `if mode in \["video", "both"]`)

\- ☁️ Deployed the web app publicly via Streamlit Community Cloud



\---



\## 🌐 Live Demo



The web app is deployed here: \*\*\[smart-parking-detector.streamlit.app](https://smart-parking-detector.streamlit.app)\*\*



No installation needed — open the link, upload a parking lot photo, draw a box over each space, and click \*\*Run Detection\*\*.



\---



\## 🎯 What Does This Do?



Given a photo (or video) of a parking lot, the system:

1\. Lets you mark where the parking spaces are (drag boxes over them — either in a desktop OpenCV window, or directly in your browser)

2\. Detects vehicles in those spaces using a combination of deep learning and classical image processing

3\. Marks each space green (empty) or red (occupied)

4\. Generates a visual dashboard, a text report, and a downloadable CSV



\---



\## 🌟 Features



\### Desktop Application (`run.py`)

\- 🖱️ Drag-and-select multiple parking spaces on a saved layout

\- 🤖 YOLOv8-based vehicle detection (car, motorcycle, bus, truck)

\- 🎥 Works on both static images and video streams

\- ↩️ Undo/reset selections, keyboard-driven controls

\- 📊 Auto-generates a visual dashboard (bar chart, pie chart, occupancy comparison) + text report + CSV log



\### Web Application (`app\_streamlit.py`) — \*added in this fork\*

\- 🌐 Runs entirely in the browser — no desktop window, no OpenCV mouse-coordinate quirks

\- 🖊️ Draw parking spaces directly on the uploaded image using an interactive canvas

\- 🔀 Hybrid detection: YOLOv8 + classical pixel-threshold analysis, so it works reliably even on

&#x20; straight-down aerial photos where pure YOLO detection fails

\- 📈 Live metrics panel (total/occupied/free/occupancy rate), pie chart, per-space data table

\- ⬇️ One-click CSV export of results



\---



\## 🚀 Quick Start



\### Option A — Use the deployed web app

Just open the \[live demo link](#-live-demo) above. No setup required.



\### Option B — Run the web app locally



```bash

git clone https://github.com/prachi463/smart-parking-detector.git

cd smart-parking-detector

pip install -r requirements\_web.txt

streamlit run app\_streamlit.py

```



\### Option C — Run the original desktop application



```bash

pip install -r requirements.txt

python run.py --image carParkImg.jpg

```



\*\*Desktop app keyboard shortcuts:\*\*

\- `D` — Detect vehicles \& generate reports

\- `S` — Save parking layout

\- `R` — Reset all selections

\- `Z` — Undo last selection

\- `Q` — Quit application



\---



\## 🔍 How It Works



\### Detection Pipeline



1\. \*\*Space marking\*\* — either drag-select in the OpenCV desktop window, or draw rectangles on the

&#x20;  browser canvas (web app)

2\. \*\*YOLOv8 inference\*\* — detects vehicle bounding boxes (car/motorcycle/bus/truck classes from COCO)

3\. \*\*Classical CV fallback\*\* (web app) — grayscale → Gaussian blur → adaptive threshold → dilation,

&#x20;  then measures the proportion of "edge" pixels inside each marked space. This mirrors the technique

&#x20;  the original desktop `main.py` uses, and is what makes detection reliable on aerial parking-lot photos

&#x20;  specifically, where YOLO's COCO training data (almost entirely street-level photography) doesn't

&#x20;  transfer well

4\. \*\*Decision\*\* — a space is marked occupied if either signal (YOLO overlap or classical pixel density)

&#x20;  flags it

5\. \*\*Reporting\*\* — annotated image, stats panel, charts, and CSV export



\### Why two detection methods?



Pretrained object detectors like YOLOv8n are trained on datasets (COCO) made up almost entirely of

ground-level and oblique-angle photos. A true bird's-eye/top-down parking lot photo looks nothing like

that training data — cars appear as small, flat rectangular shapes rather than the recognizable side/front

profiles YOLO expects. In testing, YOLOv8n consistently detected \*\*zero\*\* vehicles on the sample aerial

image included in this repo, regardless of confidence threshold or input resolution. Adding the classical

pixel-density method (used successfully in the original desktop app) restores reliable detection for this

camera angle, while keeping YOLO active as the primary method for any future images taken from a more

standard angle.



\---



\## 📁 Project Structure



smart-parking-detector/

├── app\_streamlit.py # Web app (this fork's main addition)

├── requirements\_web.txt # Dependencies for the web app

├── enhanced\_parking\_detector.py # Desktop app detection logic

├── car\_detector.py # YOLOv8-based vehicle detection

├── run.py # Desktop app CLI entry point

├── main.py # Basic classical-CV-only entry point

├── config.py # Centralized configuration

├── requirements.txt # Desktop app dependencies

├── carParkImg.jpg / carPark.mp4 # Sample data

├── reports/ # Generated reports (image mode)

└── data/ # CSV occupancy logs



\---



\## 🙏 Acknowledgments



This project is built on top of the original \*\*\[Car-Parking-Detection](https://github.com/8harath/Car-Parking-Detection)\*\*

by \*\*Bharath K\*\* (Jain Deemed to be University), created for the PNT Lab selection process at IIT Tirupati

Navishkar. The original desktop application, YOLOv8 integration, and reporting pipeline are his work;

this fork adds the Streamlit web interface, hybrid detection logic, and public deployment on top of it.



\- \*\*Original project \& desktop app\*\*: \[Bharath K](https://github.com/8harath)

\- \*\*YOLOv8 model\*\*: \[Ultralytics](https://github.com/ultralytics/ultralytics)

\- \*\*Web framework\*\*: \[Streamlit](https://streamlit.io/)



\## 📄 License



This project is licensed under the MIT License — see \[LICENSE](LICENSE) for details, consistent with

the original project's licensing.



\---



<div align="center">



\*\*Prachi Verma\*\* · B.Tech CSE (AI/ML), AKTU · \[GitHub](https://github.com/prachi463) · \[LinkedIn](https://linkedin.com/in/prachi-verma-aiml)



</div>

