"""
=============================================================
  Image Processing — annotate X-rays with OpenCV overlays
=============================================================
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

from utils.logger import setup_logger

logger = setup_logger(__name__)

# ── colour palette ─────────────────────────────────────────
COLOR_FRACTURE = (0, 0, 255)       # red
COLOR_BBOX     = (0, 255, 0)       # green
COLOR_WIRE     = (255, 200, 0)     # cyan-ish
COLOR_TEXT_BG  = (0, 0, 0)         # black
COLOR_TEXT     = (255, 255, 255)   # white
COLOR_GRID     = (100, 100, 255)   # light red


class ImageProcessor:
    """Draw bounding boxes, wireframes, and info overlays on X-rays."""

    def annotate_image(
        self,
        image_path: str,
        detection: Dict[str, Any],
        output_path: str,
    ) -> str:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")

        h, w = image.shape[:2]
        annotated = image.copy()

        # ── 1. draw scan-line wireframe overlay ────────────
        annotated = self._draw_wireframe(annotated)

        bbox = detection.get("bbox", [0, 0, w, h])
        detected = detection.get("fracture_detected", False)
        confidence = detection.get("confidence", 0)
        part_label = detection.get("body_part_label", "")
        type_info = detection.get("fracture_type_info", {})

        if detected:
            # ── 2. draw fracture bounding box ──────────────
            annotated = self._draw_bbox(annotated, bbox, confidence)

            # ── 3. draw corner brackets (wireframe) ────────
            annotated = self._draw_corner_brackets(annotated, bbox)

            # ── 4. draw crosshair at centre of bbox ───────
            annotated = self._draw_crosshair(annotated, bbox)

            # ── 5. draw heat-zone overlay ──────────────────
            annotated = self._draw_heat_overlay(annotated, bbox)

            # ── 6. label text ─────────────────────────────
            annotated = self._draw_label(
                annotated, bbox, part_label,
                type_info.get("type", ""),
                confidence,
            )

        # ── 7. header banner ──────────────────────────────
        annotated = self._draw_header(annotated, detected, confidence)

        cv2.imwrite(output_path, annotated)
        logger.info(f"Annotated image saved → {output_path}")
        return output_path

    # ────────────────────────────────────────────────────────
    # Wireframe — subtle scan-line grid
    # ────────────────────────────────────────────────────────
    @staticmethod
    def _draw_wireframe(img: np.ndarray) -> np.ndarray:
        h, w = img.shape[:2]
        overlay = img.copy()
        step = max(h // 20, 15)
        for y in range(0, h, step):
            cv2.line(overlay, (0, y), (w, y), COLOR_GRID, 1)
        for x in range(0, w, step):
            cv2.line(overlay, (x, 0), (x, h), COLOR_GRID, 1)
        return cv2.addWeighted(overlay, 0.12, img, 0.88, 0)

    # ────────────────────────────────────────────────────────
    # Bounding box
    # ────────────────────────────────────────────────────────
    @staticmethod
    def _draw_bbox(
        img: np.ndarray, bbox: List[int], conf: float
    ) -> np.ndarray:
        x1, y1, x2, y2 = bbox
        thickness = max(2, min(img.shape[0], img.shape[1]) // 200)
        cv2.rectangle(img, (x1, y1), (x2, y2), COLOR_BBOX, thickness)
        # outer glow
        overlay = img.copy()
        cv2.rectangle(overlay, (x1 - 3, y1 - 3), (x2 + 3, y2 + 3),
                      COLOR_FRACTURE, thickness + 1)
        return cv2.addWeighted(overlay, 0.35, img, 0.65, 0)

    # ────────────────────────────────────────────────────────
    # Corner brackets
    # ────────────────────────────────────────────────────────
    @staticmethod
    def _draw_corner_brackets(
        img: np.ndarray, bbox: List[int]
    ) -> np.ndarray:
        x1, y1, x2, y2 = bbox
        l = max(15, (x2 - x1) // 6)
        t = max(2, min(img.shape[:2]) // 200)
        # top-left
        cv2.line(img, (x1, y1), (x1 + l, y1), COLOR_WIRE, t)
        cv2.line(img, (x1, y1), (x1, y1 + l), COLOR_WIRE, t)
        # top-right
        cv2.line(img, (x2, y1), (x2 - l, y1), COLOR_WIRE, t)
        cv2.line(img, (x2, y1), (x2, y1 + l), COLOR_WIRE, t)
        # bottom-left
        cv2.line(img, (x1, y2), (x1 + l, y2), COLOR_WIRE, t)
        cv2.line(img, (x1, y2), (x1, y2 - l), COLOR_WIRE, t)
        # bottom-right
        cv2.line(img, (x2, y2), (x2 - l, y2), COLOR_WIRE, t)
        cv2.line(img, (x2, y2), (x2, y2 - l), COLOR_WIRE, t)
        return img

    # ────────────────────────────────────────────────────────
    # Crosshair
    # ────────────────────────────────────────────────────────
    @staticmethod
    def _draw_crosshair(img: np.ndarray, bbox: List[int]) -> np.ndarray:
        x1, y1, x2, y2 = bbox
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        r = max(8, (x2 - x1) // 8)
        cv2.drawMarker(
            img, (cx, cy), COLOR_FRACTURE,
            markerType=cv2.MARKER_CROSS, markerSize=r, thickness=1,
        )
        cv2.circle(img, (cx, cy), r, COLOR_FRACTURE, 1)
        return img

    # ────────────────────────────────────────────────────────
    # Semi-transparent red heat overlay
    # ────────────────────────────────────────────────────────
    @staticmethod
    def _draw_heat_overlay(
        img: np.ndarray, bbox: List[int]
    ) -> np.ndarray:
        x1, y1, x2, y2 = bbox
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), COLOR_FRACTURE, -1)
        return cv2.addWeighted(overlay, 0.12, img, 0.88, 0)

    # ────────────────────────────────────────────────────────
    # Text label beside bounding box
    # ────────────────────────────────────────────────────────
    @staticmethod
    def _draw_label(
        img: np.ndarray,
        bbox: List[int],
        part: str,
        ftype: str,
        conf: float,
    ) -> np.ndarray:
        x1, y1, x2, y2 = bbox
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = max(0.4, min(img.shape[:2]) / 1200)
        thick = max(1, int(scale * 2))

        lines_text = [
            f"FRACTURE DETECTED  {conf*100:.0f}%",
            f"Region: {part}",
        ]
        if ftype:
            lines_text.append(f"Type: {ftype}")

        ty = max(y1 - 10, 20)
        for i, txt in enumerate(lines_text):
            (tw, th), _ = cv2.getTextSize(txt, font, scale, thick)
            tl = (x1, ty - th - 4 + i * 0)
            br = (x1 + tw + 8, ty + 4)
            cv2.rectangle(img, tl, br, COLOR_TEXT_BG, -1)
            cv2.putText(img, txt, (x1 + 4, ty), font, scale, COLOR_TEXT, thick)
            ty += th + 12
        return img

    # ────────────────────────────────────────────────────────
    # Top banner
    # ────────────────────────────────────────────────────────
    @staticmethod
    def _draw_header(
        img: np.ndarray, detected: bool, conf: float
    ) -> np.ndarray:
        h, w = img.shape[:2]
        bar_h = max(32, h // 18)
        cv2.rectangle(img, (0, 0), (w, bar_h), COLOR_TEXT_BG, -1)

        status = "FRACTURE DETECTED" if detected else "NO FRACTURE DETECTED"
        color = (0, 100, 255) if detected else (0, 200, 100)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = max(0.45, min(w, h) / 1400)
        thick = max(1, int(scale * 2))

        cv2.putText(
            img, f"AI X-Ray Analysis  |  {status}  |  Conf: {conf*100:.0f}%",
            (8, bar_h - 10), font, scale, color, thick,
        )
        return img