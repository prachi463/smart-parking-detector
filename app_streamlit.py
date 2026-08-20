"""
Smart Parking Detector - Web Interface
----------------------------------------
A Streamlit web app that wraps the existing YOLOv8 parking detection logic
from car_detector.py in a browser-based UI, plus a Vehicle Registration
module (SQLite-backed) for logging who is parked where.

HOW TO RUN:
1. Place this file in your project folder (same folder as run.py)
2. Install the extra requirements:
       pip install -r requirements_web.txt
3. Run:
       streamlit run app_streamlit.py
   This will open a browser tab automatically (usually http://localhost:8501)

NOTE ON THE REGISTRATION DATABASE:
This uses a local SQLite file (parking.db) created next to this script.
On Streamlit Community Cloud, the filesystem is ephemeral, so registered
vehicles persist while the app is running/awake but may reset after the
app restarts or redeploys. For local/desktop use this is fully persistent.
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import cv2
import pandas as pd
import matplotlib.pyplot as plt
from ultralytics import YOLO
import sqlite3
from datetime import datetime

# ---------- Page setup ----------
st.set_page_config(page_title="Smart Parking Detector", page_icon="🅿️", layout="wide")

st.title("🅿️ Smart Parking Space Detector")
st.caption("Powered by YOLOv8 · Detect free/occupied spaces, and register vehicles against parking slots.")

DB_NAME = "parking.db"


# ============================================================
# DATABASE (Vehicle Registration)
# ============================================================

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT,
            vehicle_number TEXT NOT NULL UNIQUE,
            vehicle_type TEXT NOT NULL,
            vehicle_model TEXT,
            vehicle_color TEXT,
            parking_slot TEXT,
            entry_time TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def validate_mobile(mobile: str) -> bool:
    return mobile.isdigit() and len(mobile) == 10


def validate_vehicle_number(number: str) -> bool:
    """Basic vehicle-number sanity check, e.g. UP78AB1234, DL01CA1234."""
    number = number.replace(" ", "").upper()
    if len(number) < 8 or len(number) > 12:
        return False
    return number.isalnum()


def insert_vehicle(owner_name, mobile, email, vehicle_number, vehicle_type, model, color, slot):
    entry_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO vehicles
                (owner_name, mobile, email, vehicle_number, vehicle_type, vehicle_model, vehicle_color, parking_slot, entry_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (owner_name, mobile, email, vehicle_number, vehicle_type, model, color, slot, entry_time),
        )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, f"Vehicle {vehicle_number} is already registered."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_vehicles(search_text: str = "") -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    if search_text:
        value = f"%{search_text}%"
        query = """
            SELECT id, owner_name AS "Owner", mobile AS "Mobile", email AS "Email",
                   vehicle_number AS "Vehicle No", vehicle_type AS "Type",
                   vehicle_model AS "Model", vehicle_color AS "Color",
                   parking_slot AS "Slot", entry_time AS "Entry Time"
            FROM vehicles
            WHERE owner_name LIKE ? OR mobile LIKE ? OR vehicle_number LIKE ?
               OR vehicle_model LIKE ? OR parking_slot LIKE ?
            ORDER BY id DESC
        """
        df = pd.read_sql_query(query, conn, params=(value, value, value, value, value))
    else:
        query = """
            SELECT id, owner_name AS "Owner", mobile AS "Mobile", email AS "Email",
                   vehicle_number AS "Vehicle No", vehicle_type AS "Type",
                   vehicle_model AS "Model", vehicle_color AS "Color",
                   parking_slot AS "Slot", entry_time AS "Entry Time"
            FROM vehicles
            ORDER BY id DESC
        """
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def delete_vehicle(vehicle_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()


create_database()

# ---------- Load YOLOv8 model once (cached across reruns) ----------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

with st.spinner("Loading YOLOv8 model..."):
    model = load_model()

CAR_CLASSES = [2, 3, 5, 7]  # COCO ids: car, motorcycle, bus, truck


# ============================================================
# TABS
# ============================================================
tab_detect, tab_register = st.tabs(["🅿️ Parking Detection", "🚗 Vehicle Registration"])


# ============================================================
# TAB 1 — PARKING DETECTION (unchanged from before)
# ============================================================
with tab_detect:
    st.sidebar.header("1. Upload Image")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a parking lot image", type=["jpg", "jpeg", "png"], key="detect_upload"
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

    if uploaded_file is None:
        st.info("👈 Upload a parking lot image from the sidebar to get started.")
    else:
        image = Image.open(uploaded_file).convert("RGB")
        img_array = np.array(image)

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
            key=f"canvas_{uploaded_file.name}_{uploaded_file.size}",
        )

        spaces = []
        if canvas_result.json_data is not None:
            for obj in canvas_result.json_data["objects"]:
                x = int(obj["left"] / scale)
                y = int(obj["top"] / scale)
                w = int(obj["width"] * obj.get("scaleX", 1) / scale)
                h = int(obj["height"] * obj.get("scaleY", 1) / scale)
                if w > 5 and h > 5:
                    spaces.append((x, y, w, h))

        st.write(f"**Marked spaces: {len(spaces)}**")

        run_clicked = st.button("🚗 Run Detection", type="primary", disabled=len(spaces) == 0)

        if run_clicked:
            with st.spinner("Running detection..."):
                results = model(img_array, conf=CONFIDENCE_THRESHOLD, imgsz=1280)[0]
                vehicle_boxes = [b for b in results.boxes if int(b.cls) in CAR_CLASSES]
                st.caption(f"YOLOv8 detected {len(vehicle_boxes)} vehicle(s) directly.")

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
                    yolo_occupied = False
                    for box in vehicle_boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        if x1 < x + w and x2 > x and y1 < y + h and y2 > y:
                            yolo_occupied = True
                            break

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


# ============================================================
# TAB 2 — VEHICLE REGISTRATION (new)
# ============================================================
with tab_register:
    st.subheader("Register a Vehicle")
    st.caption("Log a vehicle against a parking slot. Fields marked * are required.")

    VEHICLE_TYPES = ["Car", "SUV", "Sedan", "Hatchback", "Motorcycle", "Scooter", "Bus", "Truck", "Other"]
    SLOTS = [f"Slot {i}" for i in range(1, 65)]

    with st.form("register_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            owner_name = st.text_input("Owner Name *")
            vehicle_number = st.text_input("Registration Number *", help="e.g. UP78AB1234")
        with c2:
            mobile = st.text_input("Mobile Number *", help="10 digits, no spaces")
            vehicle_type = st.selectbox("Vehicle Type *", [""] + VEHICLE_TYPES)
        with c3:
            email = st.text_input("Email Address")
            parking_slot = st.selectbox("Parking Slot *", [""] + SLOTS)

        c4, c5 = st.columns(2)
        with c4:
            model_name = st.text_input("Vehicle Model *")
        with c5:
            color = st.text_input("Vehicle Color *")

        submitted = st.form_submit_button("✓ Register Vehicle", type="primary")

        if submitted:
            errors = []
            if not owner_name.strip():
                errors.append("Owner name is required.")
            if not mobile.strip():
                errors.append("Mobile number is required.")
            elif not validate_mobile(mobile.strip()):
                errors.append("Mobile number must be exactly 10 digits.")
            vnum = vehicle_number.strip().upper().replace(" ", "")
            if not vnum:
                errors.append("Vehicle registration number is required.")
            elif not validate_vehicle_number(vnum):
                errors.append("Vehicle registration number looks invalid (8-12 alphanumeric characters expected).")
            if not vehicle_type:
                errors.append("Please select a vehicle type.")
            if not model_name.strip():
                errors.append("Vehicle model is required.")
            if not color.strip():
                errors.append("Vehicle color is required.")
            if not parking_slot:
                errors.append("Please select a parking slot.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                ok, err = insert_vehicle(
                    owner_name.strip(), mobile.strip(), email.strip(), vnum,
                    vehicle_type, model_name.strip(), color.strip(), parking_slot,
                )
                if ok:
                    st.success(f"✓ Vehicle {vnum} registered successfully in {parking_slot}.")
                else:
                    st.error(err)

    st.markdown("---")
    st.subheader("Registered Vehicles")

    search_text = st.text_input("🔎 Search by name, mobile, vehicle number, model, or slot", key="search_vehicles")
    vehicles_df = get_vehicles(search_text.strip())

    st.write(f"**Total registered: {len(vehicles_df)}**")

    if len(vehicles_df):
        st.dataframe(vehicles_df.drop(columns=["id"]), width=1100)

        st.markdown("##### Delete a vehicle")
        options = {
            f"{row['Vehicle No']} — {row['Owner']} ({row['Slot']})": row["id"]
            for _, row in vehicles_df.iterrows()
        }
        choice = st.selectbox("Select a vehicle to remove", [""] + list(options.keys()))
        if st.button("🗑️ Delete Selected Vehicle", disabled=not choice):
            delete_vehicle(options[choice])
            st.success("Vehicle deleted.")
            st.rerun()

        csv = vehicles_df.drop(columns=["id"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download registered vehicles as CSV", data=csv, file_name="registered_vehicles.csv", mime="text/csv"
        )
    else:
        st.info("No vehicles registered yet — use the form above to add one.")
