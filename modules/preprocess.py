import cv2
import numpy as np


def _is_colorful(img: np.ndarray) -> bool:
    """Detecta si la imagen tiene color significativo."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return float(hsv[:, :, 1].mean()) > 25


def _enhance_bw(img: np.ndarray) -> np.ndarray:
    """Mejora imágenes en escala de grises (facturas impresas, fotocopias)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=7)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(denoised)


def _enhance_color(img: np.ndarray) -> np.ndarray:
    """Mejora imágenes a color (fotos de facturas con cámara)."""
    # Escalar si es muy pequeña (EasyOCR funciona mejor con imágenes grandes)
    h, w = img.shape[:2]
    if max(h, w) < 1000:
        scale = 1000 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale,
                         interpolation=cv2.INTER_CUBIC)

    # Reducir ruido conservando bordes
    denoised = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)

    # Convertir a gris para el OCR (EasyOCR acepta gris o color)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _deskew(img: np.ndarray) -> np.ndarray:
    """Corrige inclinación de hasta ~10 grados (foto tomada torcida)."""
    coords = np.column_stack(np.where(img < 128))
    if len(coords) < 10:
        return img
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    if abs(angle) < 0.5:   # No vale la pena corregir menos de 0.5°
        return img
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, M, (w, h),
                          flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def process_image(path: str) -> np.ndarray:
    """
    Función principal que llama app.py.
    Recibe la ruta del archivo y devuelve la imagen lista para OCR.
    """
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {path}")

    # Escalar si es demasiado grande (evita lentitud en EasyOCR)
    h, w = img.shape[:2]
    if max(h, w) > 3000:
        scale = 3000 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale,
                         interpolation=cv2.INTER_AREA)

    # Elegir pipeline según tipo de imagen
    if _is_colorful(img):
        processed = _enhance_color(img)
    else:
        processed = _enhance_bw(img)

    # Enderezar texto inclinado
    processed = _deskew(processed)

    return processed