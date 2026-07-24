import io
import pytest
from PIL import Image
import numpy as np

from app.services.image_analyzer import analyse_image


def _make_test_image(width=200, height=200, color=(255, 0, 0)) -> bytes:
    """Create a solid-color test image as bytes."""
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_gradient_image(width=300, height=300) -> bytes:
    """Create a gradient test image with varied brightness."""
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        val = int(255 * y / height)
        arr[y, :] = [val, val, val]
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestAnalyseImage:
    def test_dimensions(self):
        image_bytes = _make_test_image(400, 300)
        features = analyse_image(image_bytes)
        assert features.width == 400
        assert features.height == 300
        assert abs(features.aspect_ratio - 400 / 300) < 0.01

    def test_brightness_solid_white(self):
        image_bytes = _make_test_image(100, 100, color=(255, 255, 255))
        features = analyse_image(image_bytes)
        assert features.brightness_score > 90

    def test_brightness_solid_black(self):
        image_bytes = _make_test_image(100, 100, color=(0, 0, 0))
        features = analyse_image(image_bytes)
        assert features.brightness_score < 10

    def test_contrast_gradient(self):
        image_bytes = _make_gradient_image()
        features = analyse_image(image_bytes)
        assert features.contrast_score > 20  # gradient has contrast

    def test_contrast_solid(self):
        image_bytes = _make_test_image(100, 100, color=(128, 128, 128))
        features = analyse_image(image_bytes)
        assert features.contrast_score < 10  # solid has near-zero contrast

    def test_dominant_colors_returned(self):
        image_bytes = _make_test_image(100, 100, color=(255, 0, 0))
        features = analyse_image(image_bytes)
        assert len(features.dominant_colors) >= 1
        # dominant color should be close to red
        r, g, b = features.dominant_colors[0]
        assert r > 200

    def test_face_count_no_faces(self):
        image_bytes = _make_test_image(200, 200)
        features = analyse_image(image_bytes)
        assert features.face_count == 0

    def test_composition_score_range(self):
        image_bytes = _make_gradient_image()
        features = analyse_image(image_bytes)
        assert 0 <= features.composition_score <= 100
