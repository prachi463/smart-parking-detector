"""
Configuration file for Car Parking Detection System
All configurable parameters are centralized here for easy management
"""

from typing import Final, List, Tuple

# Parking Space Dimensions
PARKING_WIDTH: Final[int] = 107
PARKING_HEIGHT: Final[int] = 48

# Detection Thresholds
OCCUPANCY_THRESHOLD: Final[int] = 900  # Pixel count threshold for space occupancy
CONFIDENCE_THRESHOLD: Final[float] = 0.5  # Minimum confidence for vehicle detection

# YOLO Model Configuration
MODEL_PATH: Final[str] = "yolov8n.pt"
CAR_CLASSES: Final[List[int]] = [2, 3, 5, 7]  # COCO classes: cars, motorcycles, buses, trucks

# File Paths
POSITION_FILE: Final[str] = "CarParkPos"
DEFAULT_VIDEO_PATH: Final[str] = "carPark.mp4"
DEFAULT_IMAGE_PATH: Final[str] = "carParkImg.jpg"

# Directory Structure
REPORTS_DIR: Final[str] = "reports"
DATA_DIR: Final[str] = "data"
MODELS_DIR: Final[str] = "models"

# CSV Configuration
CSV_FILE: Final[str] = "parking_status.csv"
CSV_APPEND_MODE: Final[bool] = True  # Set to True to keep historical data

# UI Configuration
BORDER_SIZE: Final[int] = 50
WINDOW_NAME: Final[str] = "Parking Detection"

# Zoom Configuration
MIN_ZOOM: Final[float] = 0.5
MAX_ZOOM: Final[float] = 3.0
ZOOM_STEP: Final[float] = 0.1
PAN_STEP: Final[int] = 50

# Colors (BGR format)
COLOR_EMPTY: Final[Tuple[int, int, int]] = (0, 255, 0)  # Green
COLOR_OCCUPIED: Final[Tuple[int, int, int]] = (0, 0, 255)  # Red
COLOR_SPECIAL: Final[Tuple[int, int, int]] = (0, 255, 255)  # Yellow
COLOR_REGULAR: Final[Tuple[int, int, int]] = (255, 0, 255)  # Magenta
COLOR_SELECTION: Final[Tuple[int, int, int]] = (0, 255, 0)  # Green

# Special Parking Detection
YELLOW_PERCENTAGE_THRESHOLD: Final[int] = (
    3  # Minimum percentage of yellow pixels for special parking
)
MIN_LINE_LENGTH_RATIO: Final[float] = 0.3  # Minimum line length as ratio of space dimension

# Report Configuration
REPORT_DPI: Final[int] = 300
REPORT_FIGSIZE: Final[Tuple[int, int]] = (15, 10)
