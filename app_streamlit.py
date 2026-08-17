"""
Smart Parking Detector - Web Interface
----------------------------------------
A Streamlit web app that wraps the existing YOLOv8 parking detection logic
from car_detector.py in a browser-based UI.

HOW TO RUN:
1. Place this file in your Car-Parking-Detection-main folder (same folder as run.py)
2. Install the extra requirement:
       pip install streamlit streamlit-drawable-canvas
3. Run:
       streamlit run app_streamlit.py
   This will open a browser tab automatically (usually http://localhost:8501)

HOW TO USE:
1. Upload a parking lot image
2. Draw a rectangle over each parking space you want to monitor
3. Click "Run Detection"
4. View the annotated image, live stats, and charts
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import cv2
import pandas as pd
import matplotlib.pyplot as plt
from ultralytics import YOLO

# ---------- Page setup ----------
st.set_page_config(page_title="Smart Parking Detector", page_icon="🅿️", layout="wide")

st.title("🅿️ Smart Parking Space Detector")
st.caption("Powered by YOLOv8 · Upload an image, mark the parking spaces, and detect occupancy.")

# ---------- Load YOLOv8 model once (cached across reruns) ----------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

with st.spinner("Loading YOLOv8 model..."):
    model = load_model()

# COCO class IDs for vehicles: car, motorcycle, bus, truck
CAR_CLASSES = [2, 3, 5, 7]
CONFIDENCE_THRESHOLD = 0.3

# ---------- Sidebar ----------
st.sidebar.header("1. Upload Image")
uploaded_file = st.sidebar.file_uploader(
    "Choose a parking lot image", type=["jpg", "jpeg", "png"]
)

st.sidebar.header("2. Detection Settings")
CONFIDENCE_THRESHOLD = st.sidebar.slider(
    "Confidence threshold", min_value=0.1, max_value=0.9, value=0.3, step=0.05
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Draw a rectangle over each parking space directly on the image below, "
    "then click **Run Detection**."
)

# ---------- Main flow ----------
if uploaded_file is None:
    st.info("👈 Upload a parking lot image from the sidebar to get started.")
    st.stop()

image = Image.open(uploaded_file).convert("RGB")
img_array = np.array(image)

# Scale down very large images so the canvas fits nicely on screen
MAX_DISPLAY_WIDTH = 1000
scale = 1.0
if image.width > MAX_DISPLAY_WIDTH:
    scale = MAX_DISPLAY_WIDTH / image.width
    display_image = image.resize((int(image.width * scale), int(image.height * scale)))
else:
    display_image = image

st.subheader("Step 1 — Mark Parking Spaces")
st.caption("Click and drag to draw a box over each parking spot. Draw as many as you like.")

canvas_result = st_canvas(
    fill_color="rgba(255, 0, 255, 0.25)",
    stroke_width=2,
    stroke_color="#FF00FF",
    background_image=display_image,
    update_streamlit=True,
    height=display_image.height,
    width=display_image.width,
    drawing_mode="rect",
    key="canvas",
)

# Convert drawn rectangles back to full-resolution image coordinates
spaces = []
if canvas_result.json_data is not None:
    for obj in canvas_result.json_data["objects"]:
        x = int(obj["left"] / scale)
        y = int(obj["top"] / scale)
        w = int(obj["width"] * obj.get("scaleX", 1) / scale)
        h = int(obj["height"] * obj.get("scaleY", 1) / scale)
        if w > 5 and h > 5:  # ignore accidental tiny clicks
            spaces.append((x, y, w, h))

st.write(f"**Marked spaces: {len(spaces)}**")

run_clicked = st.button("🚗 Run Detection", type="primary", disabled=len(spaces) == 0)

if run_clicked:
    with st.spinner("Running detection..."):
        # --- YOLOv8 pass (kept as a bonus signal / for non-aerial photos) ---
        results = model(img_array, conf=CONFIDENCE_THRESHOLD, imgsz=1280)[0]
        vehicle_boxes = [b for b in results.boxes if int(b.cls) in CAR_CLASSES]
        st.caption(f"YOLOv8 detected {len(vehicle_boxes)} vehicle(s) directly.")

        # --- Classical CV pass (reliable for straight-down aerial photos, where
        # pretrained YOLO models struggle since they're trained on street-level images) ---
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 1)
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16
        )
        median = cv2.medianBlur(thresh, 5)
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(median, kernel, iterations=1)

        output_img = img_array.copy()
        space_records = []

        for (x, y, w, h) in spaces:
            # Signal 1: does a YOLO-detected vehicle box overlap this space?
            yolo_occupied = False
            for box in vehicle_boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                if x1 < x + w and x2 > x and y1 < y + h and y2 > y:
                    yolo_occupied = True
                    break

            # Signal 2: classical pixel-density check (edges/texture inside the box)
            crop = dilated[y : y + h, x : x + w]
            filled_ratio = cv2.countNonZero(crop) / float(w * h) if w * h > 0 else 0
            classical_occupied = filled_ratio > 0.18

            occupied = yolo_occupied or classical_occupied

            color = (255, 0, 0) if occupied else (0, 255, 0)
            cv2.rectangle(output_img, (x, y), (x + w, y + h), color, 3)
            space_records.append(
                {"x": x, "y": y, "width": w, "height": h, "status": "Occupied" if occupied else "Free"}
            )

    df = pd.DataFrame(space_records)
    occupied_count = int((df["status"] == "Occupied").sum())
    free_count = len(df) - occupied_count

    st.subheader("Step 2 — Results")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.image(output_img, caption="Detection Result", use_column_width=True)

    with col2:
        st.metric("Total Spaces", len(df))
        st.metric("Occupied", occupied_count)
        st.metric("Free", free_count)
        occupancy_pct = (occupied_count / len(df) * 100) if len(df) else 0
        st.metric("Occupancy Rate", f"{occupancy_pct:.1f}%")

        fig, ax = plt.subplots(figsize=(3, 3))
        if len(df):
            ax.pie(
                [occupied_count, free_count],
                labels=["Occupied", "Free"],
                colors=["#e74c3c", "#2ecc71"],
                autopct="%1.1f%%",
                startangle=90,
            )
        st.pyplot(fig)

    st.subheader("Space-by-Space Breakdown")
    st.dataframe(df, width=800)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download results as CSV", data=csv, file_name="parking_status.csv", mime="text/csv"
    )
