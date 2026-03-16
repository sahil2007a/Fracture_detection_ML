"""
=============================================================
  Translator — English → Hindi (MarianMT, with fallback)
=============================================================
"""

from typing import Optional

from ml.model_loader import ModelLoader
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ── fallback dictionary for common medical phrases ─────────
_HINDI_FALLBACK = {
    "fracture": "फ्रैक्चर",
    "bone": "हड्डी",
    "wrist": "कलाई",
    "shoulder": "कंधा",
    "elbow": "कोहनी",
    "hip": "कूल्हा",
    "knee": "घुटना",
    "ankle": "टखना",
    "spine": "रीढ़ की हड्डी",
    "rib": "पसली",
    "skull": "खोपड़ी",
    "detected": "पाया गया",
    "not detected": "नहीं पाया गया",
    "healing time": "ठीक होने का समय",
    "weeks": "सप्ताह",
    "rest": "आराम",
    "surgery": "सर्जरी",
    "mild": "हल्का",
    "moderate": "मध्यम",
    "severe": "गंभीर",
    "pain": "दर्द",
    "swelling": "सूजन",
    "treatment": "इलाज",
    "doctor": "डॉक्टर",
    "hospital": "अस्पताल",
    "x-ray": "एक्स-रे",
    "cast": "प्लास्टर",
    "splint": "स्प्लिंट",
    "physiotherapy": "फिजियोथेरेपी",
}


class Translator:
    """Translate English text to Hindi."""

    def translate(self, text: str, target: str = "hi") -> str:
        """Return translated text.  Falls back to dictionary-based if
        the MarianMT model is unavailable."""
        if target != "hi":
            return text  # only Hindi supported in MVP

        # ── try MarianMT ───────────────────────────────────
        try:
            loader = ModelLoader.get_instance()
            model, tokenizer = loader.get_translator()
            if model is not None and tokenizer is not None:
                return self._marian_translate(text, model, tokenizer)
        except Exception as exc:
            logger.warning(f"MarianMT translation failed: {exc}")

        # ── fallback: simple word-level replacement ────────
        logger.info("Using fallback dictionary translation")
        return self._fallback_translate(text)

    # ── MarianMT ───────────────────────────────────────────
    @staticmethod
    def _marian_translate(text: str, model, tokenizer) -> str:
        # split into ≤ 512-token chunks
        sentences = text.replace(". ", ".\n").split("\n")
        translated_parts = []
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            tokens = tokenizer(sent, return_tensors="pt",
                               padding=True, truncation=True,
                               max_length=512)
            output = model.generate(**tokens)
            decoded = tokenizer.decode(output[0], skip_special_tokens=True)
            translated_parts.append(decoded)
        result = " ".join(translated_parts)
        logger.info("MarianMT translation succeeded")
        return result

    # ── fallback ───────────────────────────────────────────
    @staticmethod
    def _fallback_translate(text: str) -> str:
        result = text.lower()
        for en, hi in sorted(_HINDI_FALLBACK.items(),
                             key=lambda x: -len(x[0])):
            result = result.replace(en, hi)
        return result