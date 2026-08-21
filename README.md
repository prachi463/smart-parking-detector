\# 🚗 Smart Parking Space Detector



<div align="center">



\[!\[Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

\[!\[OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green.svg)](https://opencv.org/)

\[!\[YOLOv8](https://img.shields.io/badge/YOLOv8-Latest-orange.svg)](https://github.com/ultralytics/ultralytics)

\[!\[Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red.svg)](https://streamlit.io/)

\[!\[License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)



\*\*Smart Parking Space Detector combines classical computer vision and YOLOv8 deep learning to detect parking occupancy — available both as a desktop application and a browser-based web app.\*\*



\[Live Web App](#-live-demo) •

\[Features](#-features) •

\[Quick Start](#-quick-start) •

\[How It Works](#-how-it-works) •

\[Project Architecture](#-project-architecture)



</div>



\---



\## 🎓 About This Project



\*\*Smart Parking Space Detector\*\* is a final-year B.Tech (CSE – AI/ML) project by \*\*Prachi Verma\*\*, built on

top of an open-source desktop application originally created by \*\*Bharath K\*\* (Jain Deemed to be University)

for the PNT Lab selection process at IIT Tirupati Navishkar. The original project is called

\*\*\[Car-Parking-Detection](https://github.com/8harath/Car-Parking-Detection)\*\* — that name refers to

Bharath's original repository specifically, not this project.



\*\*What I added on top of the original project:\*\*

\- 🌐 A full \*\*Streamlit web interface\*\* (`app\_streamlit.py`) — upload an image, draw parking spaces

&#x20; directly in the browser (no more clunky desktop mouse-drag setup), and get instant results

\- 🚗 A \*\*Vehicle Registration module\*\* — register owner/vehicle/slot details against a parking space,

&#x20; with search, delete, and CSV export, backed by SQLite

\- 🔀 A \*\*hybrid detection pipeline\*\* for the web app: YOLOv8 for direct vehicle detection, combined

&#x20; with a classical pixel-density fallback — since pretrained COCO-based models like YOLOv8n are

&#x20; trained almost entirely on street-level photos and struggle to recognize vehicles from a straight-down

&#x20; aerial camera angle

\- 🐛 Fixed a bug in the original desktop app's `run.py` where `--mode both` silently skipped video

&#x20; processing entirely (`if mode == "video"` → `if mode in \["video", "both"]`)

\- ☁️ Deployed the web app publicly via Streamlit Community Cloud



\---



\## 🌐 Live Demo



The Smart Parking Space Detector web app is deployed here:

\*\*\[smart-parking-detector.streamlit.app](https://smart-parking-detector.streamlit.app)\*\*



No installation needed — open the link, upload a parking lot photo, draw a box over each space, and click \*\*Run Detection\*\*.



\---



\## 🎯 What Does This Do?



Given a photo (or video) of a parking lot, Smart Parking Space Detector:

1\. Lets you mark where the parking spaces are (drag boxes over them — either in a desktop OpenCV window, or directly in your browser)

2\. Detects vehicles in those spaces using a combination of deep learning and classical image processing

3\. Marks each space green (empty) or red (occupied)

4\. Generates a visual dashboard, a text report, and a downloadable CSV

