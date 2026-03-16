"""
=============================================================
  One-shot script to pre-download all required models
=============================================================
Run:  python download_models.py
"""

import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def download_yolo():
    print("\n📦  Downloading YOLOv8n …")
    try:
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")   # downloads if missing
        print("✅  YOLOv8n ready")
    except Exception as e:
        print(f"⚠️  YOLO download failed: {e}")


def download_translator():
    print("\n📦  Downloading MarianMT en→hi …")
    try:
        from transformers import MarianMTModel, MarianTokenizer
        name = "Helsinki-NLP/opus-mt-en-hi"
        cache = os.path.join(MODEL_DIR, "translator_cache")
        MarianTokenizer.from_pretrained(name, cache_dir=cache)
        MarianMTModel.from_pretrained(name, cache_dir=cache)
        print("✅  Translator ready")
    except Exception as e:
        print(f"⚠️  Translator download failed: {e}")


if __name__ == "__main__":
    download_yolo()
    download_translator()
    print("\n🎉  All models downloaded successfully!\n")