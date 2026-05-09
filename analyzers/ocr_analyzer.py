import io
import os

from PIL import Image
import pytesseract


DEFAULT_OCR_LANG = "spa+eng"


def _configure_tesseract():
    tesseract_cmd = os.environ.get("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def extract_text_from_image(uploaded_file, lang=DEFAULT_OCR_LANG):
    if uploaded_file is None:
        return "", None

    _configure_tesseract()

    try:
        image = Image.open(io.BytesIO(uploaded_file.getvalue()))
    except Exception as exc:
        return "", f"No se pudo leer la imagen: {exc}"

    try:
        text = pytesseract.image_to_string(image, lang=lang)
    except Exception as exc:
        return "", f"Error OCR: {exc}"

    return (text or "").strip(), None
