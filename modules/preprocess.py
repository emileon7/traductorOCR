import cv2

def process_image(ruta):
    img = cv2.imread(ruta)
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {ruta}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Reducir ruido preservando bordes
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Mejorar contraste local con CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # Binarización adaptativa
    thresh = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15, 8
    )

    cv2.imwrite("debug.png", thresh)
    return thresh

