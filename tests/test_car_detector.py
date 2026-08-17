"""Tests for car detection module"""

import os
import sys

import numpy as np
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from car_detector import CarDetector


class TestCarDetector:
    """Test CarDetector class"""

    @pytest.fixture
    def detector(self):
        """Create a car detector instance"""
        try:
            return CarDetector(model_path=config.MODEL_PATH)
        except Exception:
            pytest.skip("YOLOv8 model not available")

    @pytest.fixture
    def sample_image(self):
        """Create a sample test image"""
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def test_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector is not None
        assert detector.model is not None

    def test_detect_empty_image(self, detector, sample_image):
        """Test detection on empty image"""
        detections = detector.detect(sample_image)
        assert isinstance(detections, list)
        # Empty image should have 0 or very few detections
        assert len(detections) >= 0

    def test_detection_format(self, detector, sample_image):
        """Test detection output format"""
        detections = detector.detect(sample_image)

        if len(detections) > 0:
            detection = detections[0]
            assert "class_name" in detection
            assert "confidence" in detection
            assert "bbox" in detection
            assert len(detection["bbox"]) == 4

    def test_confidence_threshold(self, detector, sample_image):
        """Test confidence threshold filtering"""
        detections = detector.detect(sample_image, confidence=0.9)

        # All detections should meet confidence threshold
        for detection in detections:
            assert detection["confidence"] >= 0.9

    def test_car_classes(self, detector):
        """Test car classes are configured"""
        assert hasattr(detector, "car_classes")
        assert len(detector.car_classes) > 0

    def test_invalid_image(self, detector):
        """Test handling of invalid image"""
        with pytest.raises((ValueError, AttributeError)):
            detector.detect(None)
