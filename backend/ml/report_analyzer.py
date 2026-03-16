"""
=============================================================
  Report Analyzer — NLP keyword / regex analysis of OCR text
=============================================================
"""

import re
from typing import Dict, Any, List

from utils.logger import setup_logger

logger = setup_logger(__name__)

# ── medical-term dictionaries ──────────────────────────────
FRACTURE_KEYWORDS = {
    "fracture", "fractured", "break", "broken", "crack",
    "fissure", "displaced", "non-displaced", "comminuted",
    "greenstick", "hairline", "stress fracture", "avulsion",
    "compression", "oblique", "transverse", "spiral",
}

BODY_PARTS = {
    "radius": "Distal Radius",
    "ulna": "Ulna",
    "humerus": "Humerus",
    "femur": "Femur",
    "tibia": "Tibia",
    "fibula": "Fibula",
    "clavicle": "Clavicle",
    "scapula": "Scapula",
    "pelvis": "Pelvis",
    "patella": "Patella",
    "ankle": "Ankle",
    "wrist": "Wrist",
    "hip": "Hip",
    "spine": "Spine",
    "vertebra": "Vertebral Body",
    "rib": "Rib",
    "metacarpal": "Metacarpal",
    "metatarsal": "Metatarsal",
    "phalanx": "Phalanx",
    "skull": "Skull",
    "mandible": "Mandible",
}

SEVERITY_TERMS = {
    "displaced": "Severe",
    "comminuted": "Severe",
    "non-displaced": "Mild",
    "hairline": "Mild",
    "greenstick": "Mild",
    "stress": "Mild",
    "spiral": "Moderate",
    "oblique": "Moderate",
    "transverse": "Moderate",
    "avulsion": "Moderate",
    "compression": "Moderate",
}


class ReportAnalyzer:
    """Extract structured medical information from OCR text."""

    def analyze(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()

        fracture_detected = any(kw in text_lower for kw in FRACTURE_KEYWORDS)
        found_parts = self._find_body_parts(text_lower)
        fracture_types = self._find_fracture_types(text_lower)
        severity = self._assess_severity(text_lower)

        location = found_parts[0] if found_parts else "Not specified"
        ftype = fracture_types[0] if fracture_types else "Unspecified fracture"

        explanation = self._build_explanation(
            fracture_detected, ftype, location, severity
        )

        return {
            "fracture_detected": fracture_detected,
            "fracture_name": ftype.title(),
            "fracture_type": ftype.title(),
            "location": location,
            "possible_causes": self._infer_causes(location, ftype),
            "precautions": self._infer_precautions(location),
            "healing_time": self._estimate_healing(ftype, severity),
            "severity": severity,
            "explanation_en": explanation,
        }

    # ── internals ──────────────────────────────────────────
    @staticmethod
    def _find_body_parts(text: str) -> List[str]:
        found = []
        for kw, label in BODY_PARTS.items():
            if kw in text:
                found.append(label)
        return found or ["Unknown region"]

    @staticmethod
    def _find_fracture_types(text: str) -> List[str]:
        types = []
        patterns = [
            "comminuted", "greenstick", "hairline", "spiral",
            "oblique", "transverse", "compression", "avulsion",
            "displaced", "non-displaced", "stress fracture",
        ]
        for p in patterns:
            if p in text:
                types.append(p)
        return types

    @staticmethod
    def _assess_severity(text: str) -> str:
        for term, sev in SEVERITY_TERMS.items():
            if term in text:
                return sev
        return "Moderate"

    @staticmethod
    def _infer_causes(location: str, ftype: str) -> List[str]:
        cause_map = {
            "Wrist": ["Fall on outstretched hand", "Sports injury"],
            "Distal Radius": ["Fall on outstretched hand"],
            "Hip": ["Fall from height", "Osteoporosis"],
            "Femur": ["High-energy trauma", "Road accident"],
            "Clavicle": ["Fall on shoulder", "Direct impact"],
            "Rib": ["Direct blow to chest", "Coughing (pathologic)"],
            "Ankle": ["Twisting injury", "Sports accident"],
            "Tibia": ["Direct impact", "Sports injury"],
            "Spine": ["Osteoporosis", "Trauma"],
        }
        return cause_map.get(location, ["Trauma", "Accidental fall"])

    @staticmethod
    def _infer_precautions(location: str) -> List[str]:
        prec_map = {
            "Wrist": ["Wear a wrist splint", "Avoid lifting heavy objects"],
            "Distal Radius": ["Immobilize the wrist", "Use ice packs"],
            "Hip": ["Bed rest", "Surgical consultation"],
            "Femur": ["Complete bed rest", "Surgical fixation likely"],
            "Clavicle": ["Use arm sling", "Avoid shoulder movement"],
            "Rib": ["Pain management", "Deep breathing exercises"],
            "Ankle": ["Avoid weight bearing", "Use crutches"],
        }
        return prec_map.get(location, [
            "Rest the affected area", "Consult an orthopaedic specialist",
        ])

    @staticmethod
    def _estimate_healing(ftype: str, severity: str) -> str:
        if severity == "Severe":
            return "8-16 weeks"
        if severity == "Mild":
            return "3-6 weeks"
        return "4-8 weeks"

    @staticmethod
    def _build_explanation(
        detected: bool, ftype: str, location: str, severity: str
    ) -> str:
        if not detected:
            return (
                "Based on the report, no clear fracture was identified. "
                "However, please consult a radiologist for confirmation."
            )
        return (
            f"The report indicates a {ftype} in the {location} region. "
            f"The severity appears to be {severity.lower()}. "
            f"Proper medical evaluation and follow-up imaging are recommended."
        )