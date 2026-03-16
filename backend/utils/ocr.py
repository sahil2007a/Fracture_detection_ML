"""
=============================================================
  OCR Engine — extract text from scanned report images
=============================================================
"""

import os

from utils.logger import setup_logger

logger = setup_logger(__name__)


class OCREngine:
    """Wrapper around pytesseract (primary) with plain-text fallback."""

    def extract_text(self, image_path: str) -> str:
        if not os.path.exists(image_path):
            raise FileNotFoundError(image_path)

        # ── attempt pytesseract ────────────────────────────
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang="eng")
            if text.strip():
                logger.info("OCR (pytesseract) succeeded")
                return text
        except ImportError:
            logger.warning("pytesseract not installed — trying easyocr")
        except Exception as exc:
            logger.warning(f"pytesseract error: {exc}")

        # ── attempt easyocr ────────────────────────────────
        try:
            import easyocr

            reader = easyocr.Reader(["en"], gpu=False)
            results = reader.readtext(image_path, detail=0)
            text = "\n".join(results)
            if text.strip():
                logger.info("OCR (easyocr) succeeded")
                return text
        except ImportError:
            logger.warning("easyocr not installed")
        except Exception as exc:
            logger.warning(f"easyocr error: {exc}")

        return ""