import pytest
from PIL import Image
from app.services.fabric_detection_service import (
    MockFabricDetectionService, VisionFabricDetectionService, get_fabric_detection_service, SUPPORTED_FABRIC_CLASSES
)

@pytest.fixture
def sample_image_path(tmp_path):
    img_path = str(tmp_path / "cotton_swatch.png")
    img = Image.new("RGB", (120, 120), color=(200, 220, 240))
    img.save(img_path)
    return img_path

@pytest.fixture
def lowconf_image_path(tmp_path):
    img_path = str(tmp_path / "lowconf_blurry.jpg")
    img = Image.new("RGB", (30, 30), color=(100, 100, 100))
    img.save(img_path)
    return img_path

def test_mock_service_schema_compliance(sample_image_path):
    service = MockFabricDetectionService()
    result = service.analyze(sample_image_path)

    assert result.detected_fabric in SUPPORTED_FABRIC_CLASSES
    assert 0.0 <= result.confidence_score <= 0.95  # Never 100%
    assert isinstance(result.alternative_possible_fabrics, list)
    assert len(result.alternative_possible_fabrics) > 0
    assert len(result.dominant_colors) > 0
    assert result.texture in ["smooth", "rough", "ribbed", "fuzzy", "woven", "knitted", "shiny"]
    assert result.material_properties.thickness in ["light", "medium", "heavy"]
    assert result.material_properties.stretch in ["low", "medium", "high"]
    assert "AI-estimated" in result.sustainability_note or "burn/chemical" in result.sustainability_note

def test_low_confidence_threshold(lowconf_image_path):
    service = MockFabricDetectionService()
    result = service.analyze(lowconf_image_path)

    assert result.confidence_score < 0.50
    assert "Unable to identify confidently" in result.sustainability_note
    assert len(result.alternative_possible_fabrics) >= 3

def test_factory_function():
    svc_mock = get_fabric_detection_service(provider="mock")
    assert isinstance(svc_mock, MockFabricDetectionService)
