import io

import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from app.models.schemas import CvFeatures


def _get_dominant_colors(image: Image.Image, n_colors: int = 5) -> list[list[int]]:
    """Extract dominant colors via k-means clustering on downsampled pixels."""
    small = image.resize((100, 100))
    pixels = np.array(small).reshape(-1, 3)
    n_colors = min(n_colors, len(np.unique(pixels, axis=0)))
    if n_colors < 1:
        return [[0, 0, 0]]
    kmeans = KMeans(n_clusters=n_colors, n_init=5, random_state=42)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int).tolist()
    # Sort by frequency (cluster size)
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    sorted_idx = np.argsort(-counts)
    return [colors[i] for i in sorted_idx]


def _brightness_score(image: Image.Image) -> float:
    """Mean luminance of grayscale conversion, scaled to 0-100."""
    gray = image.convert("L")
    arr = np.array(gray)
    return float(arr.mean() / 255.0 * 100)


def _contrast_score(image: Image.Image) -> float:
    """Standard deviation of luminance, scaled to 0-100."""
    gray = image.convert("L")
    arr = np.array(gray)
    std = float(arr.std())
    return min(100.0, std / 128.0 * 100)  # 128 is max std for 0-255


def _face_count(cv_image: np.ndarray) -> int:
    """Count faces using OpenCV Haar cascade."""
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces)


def _detect_text(image: Image.Image) -> tuple[bool, str]:
    """Detect text on image via pytesseract. Returns (has_text, detected_text)."""
    try:
        import pytesseract
        text = pytesseract.image_to_string(image, timeout=5).strip()
        has_text = len(text) > 5  # filter noise
        return has_text, text if has_text else ""
    except Exception:
        return False, ""


def _composition_score(image: Image.Image) -> float:
    """Rule-of-thirds approximation. Checks if visual interest
    (high-variance regions) falls near the 4 intersection points."""
    gray = np.array(image.convert("L").resize((150, 150)), dtype=float)
    h, w = gray.shape

    # Compute local variance in 15x15 patches
    patch_size = 15
    interest_map = np.zeros((h // patch_size, w // patch_size))
    for i in range(interest_map.shape[0]):
        for j in range(interest_map.shape[1]):
            patch = gray[
                i * patch_size : (i + 1) * patch_size,
                j * patch_size : (j + 1) * patch_size,
            ]
            interest_map[i, j] = patch.std()

    if interest_map.max() == 0:
        return 50.0  # uniform image

    interest_map = interest_map / interest_map.max()

    # Rule-of-thirds intersection points (relative positions)
    thirds = [(1 / 3, 1 / 3), (2 / 3, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 2 / 3)]
    score = 0.0
    ih, iw = interest_map.shape
    for ry, rx in thirds:
        y, x = int(ry * ih), int(rx * iw)
        y = min(y, ih - 1)
        x = min(x, iw - 1)
        # Average interest in a small neighborhood
        y_start, y_end = max(0, y - 1), min(ih, y + 2)
        x_start, x_end = max(0, x - 1), min(iw, x + 2)
        region = interest_map[y_start:y_end, x_start:x_end]
        score += region.mean()

    # Normalize: max possible is 4.0 (all interest at intersection points)
    return min(100.0, score / 4.0 * 100)


def analyse_image(image_bytes: bytes) -> CvFeatures:
    """Extract local CV features from image bytes."""
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = pil_image.size

    # OpenCV format for face detection
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    has_text, detected_text = _detect_text(pil_image)

    return CvFeatures(
        width=width,
        height=height,
        aspect_ratio=round(width / height, 3) if height > 0 else 0,
        brightness_score=round(_brightness_score(pil_image), 1),
        contrast_score=round(_contrast_score(pil_image), 1),
        dominant_colors=_get_dominant_colors(pil_image),
        face_count=_face_count(cv_image),
        has_text_overlay=has_text,
        detected_text=detected_text,
        composition_score=round(_composition_score(pil_image), 1),
    )
