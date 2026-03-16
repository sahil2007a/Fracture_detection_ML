"""
=============================================================
  API Routes — /analyze-image  &  /analyze-report
=============================================================
"""

import os
import uuid
import time
import traceback

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from ml.fracture_detector import FractureDetector
from ml.report_analyzer import ReportAnalyzer
from ml.explanation_generator import ExplanationGenerator
from ml.translator import Translator
from utils.image_processing import ImageProcessor
from utils.ocr import OCREngine
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


# ── POST /api/analyze-image ────────────────────────────────
@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Accept an uploaded X-ray image, run fracture detection,
    generate an annotated image and structured medical output.
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] New image analysis request: {file.filename}")

    # ── validate file type ─────────────────────────────────
    allowed = {"image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. "
                   f"Allowed: {', '.join(allowed)}",
        )

    try:
        start = time.time()

        # ── save uploaded file ─────────────────────────────
        ext = os.path.splitext(file.filename or "img.png")[1] or ".png"
        upload_name = f"{request_id}{ext}"
        upload_path = os.path.join(UPLOAD_DIR, upload_name)

        contents = await file.read()
        with open(upload_path, "wb") as f:
            f.write(contents)
        logger.info(f"[{request_id}] Saved upload → {upload_path}")

        # ── fracture detection ─────────────────────────────
        detector = FractureDetector()
        detection_result = detector.detect(upload_path)
        logger.info(
            f"[{request_id}] Detection done — "
            f"fracture={detection_result['fracture_detected']}, "
            f"confidence={detection_result.get('confidence', 0):.2f}"
        )

        # ── annotate image ─────────────────────────────────
        processor = ImageProcessor()
        output_name = f"result_{request_id}.png"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        processor.annotate_image(
            upload_path,
            detection_result,
            output_path,
        )
        logger.info(f"[{request_id}] Annotated image → {output_path}")

        # ── generate explanation ───────────────────────────
        generator = ExplanationGenerator()
        analysis = generator.generate(detection_result)

        # ── translate to Hindi ─────────────────────────────
        translator = Translator()
        explanation_hi = translator.translate(
            analysis["explanation_en"], target="hi"
        )

        # ── build response ─────────────────────────────────
        elapsed = round(time.time() - start, 2)
        response = {
            "request_id": request_id,
            "fracture_detected": detection_result["fracture_detected"],
            "confidence": round(detection_result.get("confidence", 0.0), 2),
            "fracture_name": analysis["fracture_name"],
            "fracture_type": analysis["fracture_type"],
            "location": analysis["location"],
            "possible_causes": analysis["possible_causes"],
            "precautions": analysis["precautions"],
            "healing_time": analysis["healing_time"],
            "severity": analysis.get("severity", "Moderate"),
            "annotated_image": f"/outputs/{output_name}",
            "original_image": f"/uploads/{upload_name}",
            "explanation_en": analysis["explanation_en"],
            "explanation_hi": explanation_hi,
            "detection_details": detection_result.get("details", {}),
            "processing_time_sec": elapsed,
        }
        logger.info(f"[{request_id}] Response ready in {elapsed}s")
        return JSONResponse(content=response)

    except Exception as exc:
        logger.error(f"[{request_id}] Error: {exc}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(exc))


# ── POST /api/analyze-report ───────────────────────────────
@router.post("/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    """
    Accept an uploaded X-ray *report* image (scanned document),
    extract text via OCR, and perform NLP-based analysis.
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] New report analysis request: {file.filename}")

    try:
        start = time.time()

        # ── save ───────────────────────────────────────────
        ext = os.path.splitext(file.filename or "rpt.png")[1] or ".png"
        upload_name = f"report_{request_id}{ext}"
        upload_path = os.path.join(UPLOAD_DIR, upload_name)

        contents = await file.read()
        with open(upload_path, "wb") as f:
            f.write(contents)

        # ── OCR ────────────────────────────────────────────
        ocr = OCREngine()
        extracted_text = ocr.extract_text(upload_path)
        logger.info(
            f"[{request_id}] OCR extracted {len(extracted_text)} chars"
        )

        if len(extracted_text.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail="Could not extract enough text from the report image. "
                       "Please upload a clearer image.",
            )

        # ── NLP analysis ───────────────────────────────────
        analyzer = ReportAnalyzer()
        analysis = analyzer.analyze(extracted_text)

        # ── translate ──────────────────────────────────────
        translator = Translator()
        explanation_hi = translator.translate(
            analysis["explanation_en"], target="hi"
        )

        elapsed = round(time.time() - start, 2)
        response = {
            "request_id": request_id,
            "extracted_text": extracted_text[:2000],
            **analysis,
            "explanation_hi": explanation_hi,
            "processing_time_sec": elapsed,
        }
        return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[{request_id}] Error: {exc}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(exc))


# ── GET /api/health ────────────────────────────────────────
@router.get("/health")
async def health():
    return {"status": "healthy"}