import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.services.color_texture_processor import validate_image

client = TestClient(app)

def test_validate_image_oversized():
    # 11 MB dummy payload
    oversized_bytes = b"0" * (11 * 1024 * 1024)
    is_valid, msg = validate_image(oversized_bytes, "test.jpg", max_mb=10)
    assert not is_valid
    assert "exceeds maximum" in msg

def test_validate_image_unsupported_extension():
    buf = io.BytesIO()
    img = Image.new("RGB", (50, 50), color="blue")
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    is_valid, msg = validate_image(png_bytes, "test.txt", max_mb=10)
    assert not is_valid
    assert "Unsupported file format" in msg

def test_api_upload_unsupported_file_format():
    response = client.post(
        "/api/fabric-detection/analyze",
        files={"file": ("invalid_doc.pdf", b"pdf content", "application/pdf")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_api_upload_oversized_file():
    huge_bytes = b"X" * (11 * 1024 * 1024)
    response = client.post(
        "/api/fabric-detection/analyze",
        files={"file": ("large_image.jpg", huge_bytes, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "exceeds maximum" in response.json()["detail"]
