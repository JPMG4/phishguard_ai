import io
import os
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes


DEFAULT_PDF_OCR_LANG = "spa+eng"


def _configure_tesseract():
    tesseract_cmd = os.environ.get("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def _get_poppler_path():
    poppler_path = os.environ.get("POPPLER_PATH")
    return poppler_path if poppler_path else None


def extract_text_from_pdf(uploaded_file, max_pages=10, ocr_enabled=True, lang=DEFAULT_PDF_OCR_LANG):
    result = {
        "text": "",
        "error": None,
        "warnings": [],
        "pages_processed": 0,
        "pages_total": 0,
    }

    if uploaded_file is None:
        return result

    try:
        pdf_bytes = uploaded_file.getvalue()
    except Exception as exc:
        result["error"] = f"No se pudo leer el PDF: {exc}"
        return result

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            total_pages = len(pdf.pages)
            pages_to_process = min(total_pages, max_pages)

            result["pages_total"] = total_pages
            result["pages_processed"] = pages_to_process

            texts = []
            for page in pdf.pages[:pages_to_process]:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    texts.append(page_text)

    except Exception as exc:
        result["error"] = f"No se pudo leer el PDF: {exc}"
        return result

    if result["pages_total"] > result["pages_processed"]:
        result["warnings"].append(
            f"Se procesaron solo {result['pages_processed']} de {result['pages_total']} paginas."
        )

    combined_text = "\n".join(t.strip() for t in texts if t).strip()
    result["text"] = combined_text

    if ocr_enabled and not result["text"] and pdf_bytes:
        _configure_tesseract()
        try:
            images = convert_from_bytes(
                pdf_bytes,
                first_page=1,
                last_page=result["pages_processed"],
                poppler_path=_get_poppler_path(),
            )
            ocr_texts = [pytesseract.image_to_string(img, lang=lang) for img in images]
            ocr_text = "\n".join(t.strip() for t in ocr_texts if t).strip()
            result["text"] = ocr_text
        except Exception as exc:
            result["error"] = f"OCR PDF fallo: {exc}"
            return result

    if ocr_enabled and not result["text"]:
        result["warnings"].append("OCR no extrajo texto del PDF.")

    return result
