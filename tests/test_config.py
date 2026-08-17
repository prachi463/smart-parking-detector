"""Tests for configuration module"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


class TestConfig:
    """Test configuration values"""

    def test_parking_dimensions(self):
        """Test parking space dimensions are positive"""
        assert config.PARKING_WIDTH > 0
        assert config.PARKING_HEIGHT > 0

    def test_thresholds(self):
        """Test detection thresholds are valid"""
        assert config.OCCUPANCY_THRESHOLD > 0
        assert 0 < config.CONFIDENCE_THRESHOLD <= 1.0

    def test_car_classes(self):
        """Test car classes are defined"""
        assert isinstance(config.CAR_CLASSES, list)
        assert len(config.CAR_CLASSES) > 0
        assert all(isinstance(x, int) for x in config.CAR_CLASSES)

    def test_file_paths(self):
        """Test file paths are defined"""
        assert config.POSITION_FILE is not None
        assert config.DEFAULT_VIDEO_PATH is not None
        assert config.DEFAULT_IMAGE_PATH is not None

    def test_directories(self):
        """Test directory names are defined"""
        assert config.REPORTS_DIR is not None
        assert config.DATA_DIR is not None
        assert config.MODELS_DIR is not None

    def test_zoom_configuration(self):
        """Test zoom configuration is valid"""
        assert config.MIN_ZOOM < config.MAX_ZOOM
        assert config.ZOOM_STEP > 0
        assert config.PAN_STEP > 0

    def test_colors(self):
        """Test colors are defined as tuples"""
        assert isinstance(config.COLOR_EMPTY, tuple)
        assert isinstance(config.COLOR_OCCUPIED, tuple)
        assert isinstance(config.COLOR_SPECIAL, tuple)
        assert len(config.COLOR_EMPTY) == 3
        assert len(config.COLOR_OCCUPIED) == 3
