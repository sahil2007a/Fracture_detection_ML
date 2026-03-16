"""
=============================================================
  Model Loader — singleton that downloads / caches models
=============================================================
"""

import os
import threading

from utils.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")


class ModelLoader:
    """Thread-safe singleton to load heavy ML artefacts once."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.yolo_model = None
        self.translator_model = None
        self.translator_tokenizer = None
        self._loaded = False

    # ── singleton accessor ─────────────────────────────────
    @classmethod
    def get_instance(cls) -> "ModelLoader":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # ── load every model ───────────────────────────────────
    def load_all(self):
        if self._loaded:
            return
        self._load_yolo()
        self._load_translator()
        self._loaded = True

    # ── YOLO ───────────────────────────────────────────────
    def _load_yolo(self):
        try:
            from ultralytics import YOLO

            # Priority: custom fracture model → general YOLOv8n
            custom = os.path.join(MODEL_DIR, "fracture_yolov8.pt")
            if os.path.exists(custom):
                logger.info(f"Loading custom YOLO model: {custom}")
                self.yolo_model = YOLO(custom)
            else:
                logger.info("Loading YOLOv8n base model …")
                self.yolo_model = YOLO("yolov8n.pt")
            logger.info("✅  YOLO model ready")
        except Exception as exc:
            logger.warning(f"⚠️  YOLO load failed: {exc}")
            self.yolo_model = None

    # ── MarianMT translator ────────────────────────────────
    # def _load_translator(self):
    #     try:
            # from transformers import MarianMTModel, MarianTokenizer

            # model_name = "Helsinki-NLP/opus-mt-en-hi"
            # cache = os.path.join(MODEL_DIR, "translator_cache")
            # logger.info(f"Loading MarianMT ({model_name}) …")
            # self.translator_tokenizer = MarianTokenizer.from_pretrained(
            #     model_name, cache_dir=cache
            # )
            # self.translator_model = MarianMTModel.from_pretrained(
            #     model_name, cache_dir=cache
            # )
        #     logger.info("✅  Translator model ready")
        # except Exception as exc:
        #     logger.warning(f"⚠️  Translator load failed: {exc}")
        #     self.translator_model = None
        #     self.translator_tokenizer = None

    # ── accessors ──────────────────────────────────────────
    def get_yolo(self):
        if self.yolo_model is None:
            self._load_yolo()
        return self.yolo_model

    def get_translator(self):
        if self.translator_model is None:
            self._load_translator()
        return self.translator_model, self.translator_tokenizer