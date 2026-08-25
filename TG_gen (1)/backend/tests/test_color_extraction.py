import os
import pytest
from PIL import Image
from app.services.color_texture_processor import (
    extract_dominant_colors, analyze_image_texture, rgb_to_hex, get_nearest_color_name
)

@pytest.fixture
def sample_image_path(tmp_path):
    img_path = str(tmp_path / "test_fabric.jpg")
    # Create a 100x100 RGB image with half dark slate gray and half cream
    img = Image.new("RGB", (100, 100), color=(47, 79, 79))
    for x in range(50):
        for y in range(100):
            img.putpixel((x, y), (232, 220, 196))
    img.save(img_path)
    return img_path

def test_rgb_to_hex():
    assert rgb_to_hex(255, 255, 255) == "#FFFFFF"
    assert rgb_to_hex(0, 0, 0) == "#000000"
    assert rgb_to_hex(47, 79, 79) == "#2F4F4F"

def test_get_nearest_color_name():
    name = get_nearest_color_name(232, 220, 196)
    assert name in ["Cream", "Beige", "Antique White"]

def test_extract_dominant_colors(sample_image_path):
    colors = extract_dominant_colors(sample_image_path, num_colors=4)
    assert isinstance(colors, list)
    assert len(colors) > 0
    total_pct = sum(c["percentage"] for c in colors)
    assert total_pct == 100
    for c in colors:
        assert "hex" in c
        assert "name" in c
        assert "percentage" in c

def test_analyze_image_texture(sample_image_path):
    texture_info = analyze_image_texture(sample_image_path)
    assert "laplacian_var" in texture_info
    assert "roughness" in texture_info
    assert "shine" in texture_info
    assert "pattern_hint" in texture_info
