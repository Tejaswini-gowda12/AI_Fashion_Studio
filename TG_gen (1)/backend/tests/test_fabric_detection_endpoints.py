import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def valid_image_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (150, 150), color=(47, 79, 79))
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_full_fabric_detection_crud_flow(valid_image_bytes):
    # 1. POST Analyze
    res_post = client.post(
        "/api/fabric-detection/analyze",
        files={"file": ("garment_test.jpg", valid_image_bytes, "image/jpeg")}
    )
    assert res_post.status_code == 200
    data = res_post.json()
    analysis_id = data["id"]

    assert "detected_fabric" in data
    assert "confidence_score" in data
    assert "dominant_colors" in data
    assert "material_properties" in data
    assert data["confidence_score"] <= 0.95

    # 2. GET Analysis by ID
    res_get = client.get(f"/api/fabric-detection/{analysis_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == analysis_id

    # 3. PATCH User Correction
    res_patch = client.patch(
        f"/api/fabric-detection/{analysis_id}",
        json={"user_corrected_fabric": "Organic cotton"}
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["user_corrected_fabric"] == "Organic cotton"

    # 4. GET History
    res_hist = client.get("/api/fabric-detection/history")
    assert res_hist.status_code == 200
    history = res_hist.json()
    assert isinstance(history, list)
    assert any(item["id"] == analysis_id for item in history)

    # 5. DELETE Analysis
    res_del = client.delete(f"/api/fabric-detection/{analysis_id}")
    assert res_del.status_code == 200

    # 6. Verify 404 after deletion
    res_get_deleted = client.get(f"/api/fabric-detection/{analysis_id}")
    assert res_get_deleted.status_code == 404
