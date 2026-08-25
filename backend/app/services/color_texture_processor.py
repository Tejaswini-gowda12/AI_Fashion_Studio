import os
import math
from typing import List, Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image

COLOR_NAMEMAP = [
    ((47, 79, 79), "Dark Slate Gray"),
    ((232, 220, 196), "Cream"),
    ((255, 255, 255), "White"),
    ((245, 245, 220), "Beige"),
    ((0, 0, 0), "Black"),
    ((128, 128, 128), "Gray"),
    ((112, 128, 144), "Slate Gray"),
    ((25, 25, 112), "Midnight Blue"),
    ((0, 0, 128), "Navy Blue"),
    ((65, 105, 225), "Royal Blue"),
    ((70, 130, 180), "Steel Blue"),
    ((30, 144, 255), "Dodger Blue"),
    ((173, 216, 230), "Light Blue"),
    ((34, 139, 34), "Forest Green"),
    ((85, 107, 47), "Olive Green"),
    ((143, 188, 143), "Dark Sea Green"),
    ((178, 34, 34), "Firebrick Red"),
    ((165, 42, 42), "Brown"),
    ((210, 105, 30), "Chocolate"),
    ((222, 184, 135), "Burlywood"),
    ((244, 164, 96), "Sandy Brown"),
    ((218, 165, 32), "Goldenrod"),
    ((188, 143, 143), "Rosy Brown"),
    ((128, 0, 0), "Maroon"),
    ((75, 0, 130), "Indigo"),
    ((238, 130, 238), "Violet"),
    ((255, 240, 245), "Lavender Blush"),
    ((250, 235, 215), "Antique White"),
    ((139, 69, 19), "Saddle Brown"),
    ((47, 79, 79), "Charcoal"),
]

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"

def get_nearest_color_name(r: int, g: int, b: int) -> str:
    min_dist = float("inf")
    closest_name = "Custom Shade"
    for (cr, cg, cb), name in COLOR_NAMEMAP:
        dist = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
        if dist < min_dist:
            min_dist = dist
            closest_name = name
    return closest_name

def extract_dominant_colors(image_path: str, num_colors: int = 4) -> List[Dict[str, Any]]:
    """
    Uses OpenCV K-Means clustering to extract dominant colors, RGB percentages, hex, and color names.
    """
    if not os.path.exists(image_path):
        return [
            {"hex": "#2F4F4F", "name": "Dark Slate Gray", "percentage": 60},
            {"hex": "#E8DCC4", "name": "Cream", "percentage": 40}
        ]

    try:
        img = cv2.imread(image_path)
        if img is None:
            # Fallback using PIL
            pil_img = Image.open(image_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Resize for fast processing
        img_small = cv2.resize(img, (150, 150), interpolation=cv2.INTER_AREA)
        img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
        pixels = img_rgb.reshape((-1, 3)).astype(np.float32)

        # Apply K-Means
        k = min(num_colors, len(pixels))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        compactness, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, flags)

        # Count frequencies
        label_counts = np.bincount(labels.flatten())
        total_pixels = len(labels)

        colors = []
        for index in np.argsort(-label_counts):
            r, g, b = [int(c) for c in centers[index]]
            pct = int(round((label_counts[index] / total_pixels) * 100))
            if pct > 0:
                hex_code = rgb_to_hex(r, g, b)
                color_name = get_nearest_color_name(r, g, b)
                colors.append({
                    "hex": hex_code,
                    "name": color_name,
                    "percentage": pct
                })

        # Ensure percentages sum to 100%
        if colors:
            tot = sum(c["percentage"] for c in colors)
            if tot > 0 and tot != 100:
                colors[0]["percentage"] += (100 - tot)

        return colors[:num_colors]
    except Exception as e:
        print(f"Color extraction error: {e}")
        return [
            {"hex": "#2F4F4F", "name": "Dark Slate Gray", "percentage": 50},
            {"hex": "#E8DCC4", "name": "Cream", "percentage": 50}
        ]

def analyze_image_texture(image_path: str) -> Dict[str, Any]:
    """
    Analyzes visual attributes (roughness/sharpness, shine, twill diagonal angle, knit loops, pattern) using OpenCV.
    """
    if not os.path.exists(image_path):
        return {
            "laplacian_var": 120.0,
            "roughness": "medium",
            "shine": "matte",
            "texture_type": "woven",
            "pattern_hint": "solid",
            "twill_diag_score": 0.25,
            "knit_score": 0.30,
            "gabor_energy": 25000.0,
            "ortho_ratio": 0.50,
            "val_std": 35.0,
        }

    try:
        img = cv2.imread(image_path)
        if img is None:
            pil_img = Image.open(image_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 1. Laplacian variance measures high-frequency edge intensity & grain
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # 2. Value & Saturation channels measure shine/gloss and color vibrancy
        val_channel = hsv[:, :, 2]
        sat_channel = hsv[:, :, 1]
        val_std = float(np.std(val_channel))
        sat_std = float(np.std(sat_channel))
        sat_mean = float(np.mean(sat_channel))

        # 3. Directional Gradient (Sobel) to identify Twill weave vs Orthogonal Plain weave
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(sobelx**2 + sobely**2)
        angles = np.arctan2(np.abs(sobely), np.abs(sobelx)) * (180.0 / np.pi)

        edge_thresh = 25.0
        strong_edges = mag > edge_thresh
        total_strong = float(np.sum(strong_edges)) + 1e-6

        diag_mask = (angles >= 30) & (angles <= 60) & strong_edges
        ortho_mask = ((angles < 20) | (angles > 70)) & strong_edges

        twill_diag_score = float(np.sum(diag_mask) / total_strong)
        ortho_ratio = float(np.sum(ortho_mask) / total_strong)

        # 4. Multi-scale Gabor Filter Energy for Knitwear & Looped Yarn detection
        g_kernel = cv2.getGaborKernel((21, 21), 5.0, 0, 10.0, 0.5, 0, ktype=cv2.CV_32F)
        filtered = cv2.filter2D(gray, cv2.CV_32F, g_kernel)
        gabor_energy = float(np.var(filtered))

        # Knit looped score combining Gabor variance + edge density + low gloss
        knit_score = min(1.0, max(0.0, (gabor_energy / 80000.0) * 0.6 + (laplacian_var / 800.0) * 0.4))

        # Roughness categorization
        if laplacian_var > 450 or gabor_energy > 70000:
            roughness = "rough"
            texture_type = "knitted / chunky"
        elif laplacian_var > 150 or gabor_energy > 30000:
            roughness = "medium"
            texture_type = "woven / ribbed"
        else:
            roughness = "smooth"
            texture_type = "smooth"

        # Shine categorization
        # High specular shine has high value variance with bright cluster highlights
        p95_val = np.percentile(val_channel, 95)
        p50_val = np.percentile(val_channel, 50)
        specular_ratio = (p95_val - p50_val)

        if (val_std > 62 and sat_std < 55) or specular_ratio > 75:
            shine = "glossy"
        elif val_std > 42 or specular_ratio > 50:
            shine = "semi-gloss"
        else:
            shine = "matte"

        # Pattern hint
        if (laplacian_var > 600 and twill_diag_score < 0.25) or sat_std > 65:
            pattern_hint = "patterned"
        elif twill_diag_score > 0.35:
            pattern_hint = "twill weave"
        else:
            pattern_hint = "solid"

        return {
            "laplacian_var": round(laplacian_var, 2),
            "roughness": roughness,
            "texture_type": texture_type,
            "shine": shine,
            "pattern_hint": pattern_hint,
            "twill_diag_score": round(twill_diag_score, 3),
            "knit_score": round(knit_score, 3),
            "gabor_energy": round(gabor_energy, 1),
            "ortho_ratio": round(ortho_ratio, 3),
            "val_std": round(val_std, 2),
            "sat_mean": round(sat_mean, 2),
        }
    except Exception as e:
        print(f"Texture analysis error: {e}")
        return {
            "laplacian_var": 100.0,
            "roughness": "medium",
            "texture_type": "smooth",
            "shine": "matte",
            "pattern_hint": "solid",
            "twill_diag_score": 0.25,
            "knit_score": 0.30,
            "gabor_energy": 25000.0,
            "ortho_ratio": 0.50,
            "val_std": 35.0,
        }

def validate_image(file_bytes: bytes, filename: str, max_mb: int = 10) -> Tuple[bool, str]:
    """
    Validates file format and size.
    Supported: JPG, JPEG, PNG, WebP
    Max size: max_mb MB
    """
    max_bytes = max_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        return False, f"File size exceeds maximum allowed limit of {max_mb} MB."

    ext = os.path.splitext(filename.lower())[1]
    allowed_exts = [".jpg", ".jpeg", ".png", ".webp"]
    if ext not in allowed_exts:
        return False, f"Unsupported file format '{ext}'. Allowed formats: JPG, JPEG, PNG, WebP."

    try:
        from io import BytesIO
        img = Image.open(BytesIO(file_bytes))
        img.verify()
    except Exception:
        return False, "Corrupt or invalid image file."

    return True, "Valid"
