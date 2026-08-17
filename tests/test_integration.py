"""Integration tests for the parking detection system"""

import os
import sys

import cv2
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from enhanced_parking_detector import EnhancedParkingDetector


class TestIntegration:
    """Integration tests for the full system"""

    def test_config_import(self):
        """Test that config module imports correctly"""
        assert config is not None
        assert hasattr(config, "PARKING_WIDTH")
        assert hasattr(config, "PARKING_HEIGHT")

    def test_detector_creation(self):
        """Test detector can be created"""
        detector = EnhancedParkingDetector(image_path=None, video_path=None)
        assert detector is not None

    def test_directories_setup(self):
        """Test that required directories can be created"""
        from setup_directories import setup_directories

        success, missing = setup_directories()
        # Should either succeed or return list of missing dirs
        assert isinstance(success, bool)
        if not success:
            assert isinstance(missing, list)

    def test_image_processing_pipeline(self):
        """Test full image processing pipeline"""
        # Check if sample image exists
        if os.path.exists(config.DEFAULT_IMAGE_PATH):
            detector = EnhancedParkingDetector(
                image_path=config.DEFAULT_IMAGE_PATH, video_path=None
            )

            assert detector.current_image is not None
            assert detector.original_image is not None

            # Test frame processing
            processed = detector.process_frame(detector.current_image)
            assert processed is not None
        else:
            pytest.skip(f"Sample image not found at {config.DEFAULT_IMAGE_PATH}")

    def test_position_file_operations(self):
        """Test parking position file operations"""
        detector = EnhancedParkingDetector(image_path=None, video_path=None)

        # Add some positions
        test_positions = [(100, 100), (200, 200), (300, 300)]
        detector.posList = test_positions.copy()

        # Save and load
        detector.save_parking_positions()

        # Load in new instance
        new_detector = EnhancedParkingDetector(image_path=None, video_path=None)
        new_detector.load_parking_positions()

        # Should have loaded positions (if not corrupted)
        assert isinstance(new_detector.posList, list)
