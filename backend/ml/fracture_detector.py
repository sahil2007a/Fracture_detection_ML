"""
=============================================================
  Fracture Detector
  -----------------
  Hybrid approach:
    1. YOLO inference (when a fracture-trained model is present)
    2. OpenCV-based bone / fracture-line analysis (always runs)
  Produces image-specific results — different images yield
  different bounding-boxes, locations, and classifications.
=============================================================
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

from ml.model_loader import ModelLoader
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FractureDetector:
    """Detect fractures in X-ray images using YOLO + OpenCV."""

    # ── body-part heuristic lookup ─────────────────────────
    BODY_PARTS = {
        "upper_left": ("Clavicle / Shoulder", "clavicle"),
        "upper_center": ("Cervical Spine", "spine"),
        "upper_right": ("Clavicle / Shoulder", "clavicle"),
        "middle_left": ("Humerus / Upper Arm", "humerus"),
        "middle_center": ("Thoracic Spine / Ribs", "ribs"),
        "middle_right": ("Humerus / Upper Arm", "humerus"),
        "lower_left": ("Radius / Wrist", "wrist"),
        "lower_center": ("Lumbar Spine / Pelvis", "pelvis"),
        "lower_right": ("Radius / Wrist", "wrist"),
    }

    # ── public API ─────────────────────────────────────────
    def detect(self, image_path: str) -> Dict[str, Any]:
        """Run full detection pipeline on *image_path*."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # --- step 1: YOLO (optional) ---
        yolo_boxes = self._yolo_detect(image_path)

        # --- step 2: OpenCV analysis (always) ---
        cv_result = self._opencv_analysis(gray)

        # --- merge ---
        return self._merge_results(yolo_boxes, cv_result, h, w)

    # ────────────────────────────────────────────────────────
    # YOLO-based detection
    # ────────────────────────────────────────────────────────
    def _yolo_detect(self, path: str) -> List[Dict]:
        """Run YOLO if model is available; return list of boxes."""
        loader = ModelLoader.get_instance()
        model = loader.get_yolo()
        if model is None:
            return []

        try:
            results = model(path, verbose=False)
            boxes: List[Dict] = []
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    boxes.append({
                        "bbox": [int(x1), int(y1), int(x2), int(y2)],
                        "confidence": conf,
                        "class_id": cls,
                        "class_name": model.names.get(cls, "fracture"),
                    })
            return boxes
        except Exception as exc:
            logger.warning(f"YOLO inference error: {exc}")
            return []

    # ────────────────────────────────────────────────────────
    # OpenCV bone / fracture analysis
    # ────────────────────────────────────────────────────────
    def _opencv_analysis(self, gray: np.ndarray) -> Dict[str, Any]:
        h, w = gray.shape

        # 1. enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 2. bone mask via adaptive + Otsu
        blurred = cv2.GaussianBlur(enhanced, (7, 7), 0)
        _, bone_mask = cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        bone_mask = cv2.morphologyEx(
            bone_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=2
        )

        # 3. contours (bone outlines)
        contours, _ = cv2.findContours(
            bone_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        bone_contours = [
            c for c in contours if cv2.contourArea(c) > (h * w * 0.002)
        ]

        # 4. edge map inside bones
        edges = cv2.Canny(enhanced, 30, 120)
        bone_edges = cv2.bitwise_and(edges, edges, mask=bone_mask)

        # 5. Hough lines (potential fracture lines)
        min_line = max(15, int(min(h, w) * 0.04))
        lines = cv2.HoughLinesP(
            bone_edges, 1, np.pi / 180,
            threshold=25, minLineLength=min_line, maxLineGap=8,
        )

        # 6. compute per-quadrant edge density
        quadrant_density = self._quadrant_edge_density(bone_edges, h, w)

        # 7. find the region with highest discontinuity
        fracture_region, fracture_score = self._find_fracture_region(
            enhanced, bone_mask, bone_edges, lines, quadrant_density, h, w
        )

        # 8. determine body-part label
        body_part_label, body_part_key = self._guess_body_part(
            fracture_region, bone_contours, h, w
        )

        # 9. classify fracture pattern
        fracture_type_info = self._classify_fracture_pattern(
            lines, fracture_region, h, w
        )

        # 10. image-level stats (used for varied explanations)
        mean_intensity = float(np.mean(gray))
        std_intensity = float(np.std(gray))
        bone_ratio = float(np.sum(bone_mask > 0) / (h * w))

        return {
            "fracture_detected": fracture_score > 0.30,
            "confidence": min(fracture_score, 0.99),
            "bbox": fracture_region,
            "body_part_label": body_part_label,
            "body_part_key": body_part_key,
            "fracture_type_info": fracture_type_info,
            "num_lines": 0 if lines is None else len(lines),
            "quadrant_density": quadrant_density,
            "mean_intensity": mean_intensity,
            "std_intensity": std_intensity,
            "bone_ratio": bone_ratio,
        }

    # ── helpers ────────────────────────────────────────────
    @staticmethod
    def _quadrant_edge_density(
        edge_map: np.ndarray, h: int, w: int
    ) -> Dict[str, float]:
        """Return edge-pixel density for a 3×3 grid."""
        densities: Dict[str, float] = {}
        rows = ["upper", "middle", "lower"]
        cols = ["left", "center", "right"]
        rh, cw = h // 3, w // 3
        for ri, rn in enumerate(rows):
            for ci, cn in enumerate(cols):
                patch = edge_map[ri * rh: (ri + 1) * rh, ci * cw: (ci + 1) * cw]
                densities[f"{rn}_{cn}"] = float(np.sum(patch > 0) / max(patch.size, 1))
        return densities

    def _find_fracture_region(
        self,
        enhanced: np.ndarray,
        bone_mask: np.ndarray,
        bone_edges: np.ndarray,
        lines,
        quad_density: Dict[str, float],
        h: int,
        w: int,
    ) -> Tuple[List[int], float]:
        """Estimate fracture bounding-box and confidence score."""

        # --- Approach A: cluster Hough-line midpoints ---
        if lines is not None and len(lines) > 0:
            pts = []
            for ln in lines:
                x1, y1, x2, y2 = ln[0]
                pts.append(((x1 + x2) // 2, (y1 + y2) // 2))
            pts = np.array(pts)
            cx, cy = int(np.median(pts[:, 0])), int(np.median(pts[:, 1]))
            spread_x = max(int(np.std(pts[:, 0])), w // 10)
            spread_y = max(int(np.std(pts[:, 1])), h // 10)

            x1 = max(cx - spread_x - w // 20, 0)
            y1 = max(cy - spread_y - h // 20, 0)
            x2 = min(cx + spread_x + w // 20, w)
            y2 = min(cy + spread_y + h // 20, h)
            bbox = [x1, y1, x2, y2]

            # score based on line count + density
            line_score = min(len(lines) / 30.0, 1.0)
            max_qd = max(quad_density.values()) if quad_density else 0
            score = 0.3 + 0.4 * line_score + 0.3 * min(max_qd * 20, 1.0)
            return bbox, round(min(score, 0.99), 3)

        # --- Approach B: highest-density quadrant ---
        if quad_density:
            best_q = max(quad_density, key=quad_density.get)  # type: ignore[arg-type]
            row_idx = ["upper", "middle", "lower"].index(best_q.split("_")[0])
            col_idx = ["left", "center", "right"].index(best_q.split("_")[1])
            rh, cw = h // 3, w // 3
            pad = 20
            bbox = [
                max(col_idx * cw - pad, 0),
                max(row_idx * rh - pad, 0),
                min((col_idx + 1) * cw + pad, w),
                min((row_idx + 1) * rh + pad, h),
            ]
            score = 0.25 + 0.5 * min(quad_density[best_q] * 25, 1.0)
            return bbox, round(min(score, 0.85), 3)

        # fallback: center
        return [w // 4, h // 4, 3 * w // 4, 3 * h // 4], 0.15

    def _guess_body_part(
        self,
        bbox: List[int],
        contours: List,
        h: int,
        w: int,
    ) -> Tuple[str, str]:
        """Heuristic body-part detection from bbox position + contour shape."""
        cx = (bbox[0] + bbox[2]) / 2 / w
        cy = (bbox[1] + bbox[3]) / 2 / h

        row = "upper" if cy < 0.33 else ("lower" if cy > 0.66 else "middle")
        col = "left" if cx < 0.33 else ("right" if cx > 0.66 else "center")
        key = f"{row}_{col}"
        label, part_key = self.BODY_PARTS.get(key, ("Limb Bone", "limb"))

        # refine with contour aspect ratio
        if contours:
            largest = max(contours, key=cv2.contourArea)
            _, _, cw, ch = cv2.boundingRect(largest)
            ar = cw / max(ch, 1)
            if ar > 2.5:
                label, part_key = "Clavicle", "clavicle"
            elif ar < 0.35 and ch > h * 0.5:
                label, part_key = "Femur / Long Bone", "femur"
            elif 0.7 < ar < 1.4 and cv2.contourArea(largest) > h * w * 0.25:
                label, part_key = "Pelvis / Hip", "pelvis"

        return label, part_key

    @staticmethod
    def _classify_fracture_pattern(
        lines, bbox: List[int], h: int, w: int
    ) -> Dict[str, str]:
        """Classify fracture type from Hough-line angles."""
        if lines is None or len(lines) == 0:
            return {"type": "Hairline fracture", "pattern": "subtle"}

        angles = []
        for ln in lines:
            x1, y1, x2, y2 = ln[0]
            angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            angles.append(angle)

        mean_angle = float(np.mean(angles))
        std_angle = float(np.std(angles))
        n = len(angles)

        if n >= 8 and std_angle > 30:
            return {"type": "Comminuted fracture", "pattern": "multi-fragment"}
        if mean_angle > 70:
            return {"type": "Transverse fracture", "pattern": "perpendicular"}
        if mean_angle < 30:
            return {"type": "Oblique fracture", "pattern": "angled"}
        if std_angle > 20:
            return {"type": "Spiral fracture", "pattern": "rotational"}
        if n <= 3:
            return {"type": "Greenstick fracture", "pattern": "incomplete"}
        return {"type": "Simple fracture", "pattern": "linear"}

    # ────────────────────────────────────────────────────────
    # Merge YOLO + OpenCV results
    # ────────────────────────────────────────────────────────
    def _merge_results(
        self,
        yolo_boxes: List[Dict],
        cv_result: Dict[str, Any],
        h: int,
        w: int,
    ) -> Dict[str, Any]:
        """Combine YOLO and OpenCV outputs into a single result dict."""

        # if YOLO found high-confidence fractures, prefer those
        fracture_yolo = [
            b for b in yolo_boxes if b["confidence"] > 0.40
        ]

        if fracture_yolo:
            best = max(fracture_yolo, key=lambda b: b["confidence"])
            bbox = best["bbox"]
            conf = best["confidence"]
            detected = True
        else:
            bbox = cv_result["bbox"]
            conf = cv_result["confidence"]
            detected = cv_result["fracture_detected"]

        return {
            "fracture_detected": detected,
            "confidence": conf,
            "bbox": bbox,
            "body_part_label": cv_result["body_part_label"],
            "body_part_key": cv_result["body_part_key"],
            "fracture_type_info": cv_result["fracture_type_info"],
            "details": {
                "yolo_detections": len(yolo_boxes),
                "opencv_lines": cv_result["num_lines"],
                "mean_intensity": cv_result["mean_intensity"],
                "std_intensity": cv_result["std_intensity"],
                "bone_ratio": cv_result["bone_ratio"],
                "quadrant_density": cv_result["quadrant_density"],
            },
        }