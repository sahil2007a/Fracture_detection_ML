"""
=============================================================
  Explanation Generator
  ---------------------
  Maps detection results to structured, patient-friendly
  medical insights.  Uses image-derived features so that
  different images produce different outputs.
=============================================================
"""

from typing import Dict, Any, List

from utils.logger import setup_logger

logger = setup_logger(__name__)

# ── knowledge base ─────────────────────────────────────────
FRACTURE_DB: Dict[str, Dict[str, Any]] = {
    "clavicle": {
        "names": ["Clavicle fracture", "Broken collarbone"],
        "causes": [
            "Fall on outstretched hand",
            "Direct blow to shoulder",
            "Sports collision",
        ],
        "precautions": [
            "Use an arm sling for support",
            "Avoid lifting heavy objects",
            "Apply ice packs to reduce swelling",
            "Take prescribed pain medication",
        ],
        "healing": {"Mild": "4-6 weeks", "Moderate": "6-8 weeks", "Severe": "8-12 weeks"},
        "explanation": (
            "This X-ray shows a fracture in the clavicle (collarbone). "
            "This usually happens from a fall onto the shoulder or a direct hit. "
            "With rest and an arm sling, it typically heals well."
        ),
    },
    "humerus": {
        "names": ["Humerus fracture", "Upper arm fracture"],
        "causes": [
            "Fall on elbow or outstretched hand",
            "Direct trauma to upper arm",
            "Twisting force",
        ],
        "precautions": [
            "Immobilize with a splint or sling",
            "Avoid rotating the arm",
            "Consult an orthopaedic surgeon",
        ],
        "healing": {"Mild": "6-8 weeks", "Moderate": "8-12 weeks", "Severe": "12-16 weeks"},
        "explanation": (
            "A fracture is visible in the humerus (upper arm bone). "
            "This can happen from a fall or direct impact. "
            "Treatment usually involves immobilization, "
            "and surgery may be needed for displaced fractures."
        ),
    },
    "wrist": {
        "names": ["Colles' fracture", "Distal radius fracture", "Smith's fracture"],
        "causes": [
            "Fall on outstretched hand",
            "Sports injury",
            "Osteoporosis-related weakness",
        ],
        "precautions": [
            "Immobilize the wrist with a cast",
            "Avoid heavy lifting for 6 weeks",
            "Apply ice to reduce swelling",
            "Keep the hand elevated",
        ],
        "healing": {"Mild": "4-6 weeks", "Moderate": "6-8 weeks", "Severe": "8-12 weeks"},
        "explanation": (
            "This X-ray shows a fracture near the wrist in the distal radius bone. "
            "This is one of the most common fractures, usually caused by falling "
            "on an outstretched hand. With proper casting and rest, "
            "it generally heals within 4 to 8 weeks."
        ),
    },
    "ribs": {
        "names": ["Rib fracture", "Broken rib"],
        "causes": [
            "Direct blow to the chest",
            "Fall onto a hard surface",
            "Severe coughing (stress fracture)",
        ],
        "precautions": [
            "Take pain medication as prescribed",
            "Practice deep breathing exercises",
            "Avoid wrapping the chest tightly",
            "Rest and avoid strenuous activity",
        ],
        "healing": {"Mild": "3-4 weeks", "Moderate": "4-6 weeks", "Severe": "6-10 weeks"},
        "explanation": (
            "The X-ray indicates a rib fracture. "
            "Rib fractures are painful but usually heal on their own with rest. "
            "Pain management and breathing exercises are important "
            "to prevent lung complications."
        ),
    },
    "spine": {
        "names": ["Vertebral compression fracture", "Spinal fracture"],
        "causes": [
            "Osteoporosis",
            "High-energy trauma",
            "Fall from height",
        ],
        "precautions": [
            "Strict bed rest initially",
            "Wear a back brace",
            "Consult a spine specialist immediately",
            "Avoid bending or twisting",
        ],
        "healing": {"Mild": "6-8 weeks", "Moderate": "8-12 weeks", "Severe": "12-20 weeks"},
        "explanation": (
            "A fracture is detected in the spinal region. "
            "This could be a compression fracture and needs careful evaluation. "
            "Please consult a spine specialist for further imaging and treatment."
        ),
    },
    "pelvis": {
        "names": ["Pelvic fracture", "Hip fracture", "Femoral neck fracture"],
        "causes": [
            "Fall from height",
            "Road traffic accident",
            "Osteoporosis in elderly",
        ],
        "precautions": [
            "Complete bed rest",
            "Surgical consultation recommended",
            "Avoid weight bearing on affected side",
            "Physiotherapy after healing",
        ],
        "healing": {"Mild": "6-8 weeks", "Moderate": "8-12 weeks", "Severe": "12-24 weeks"},
        "explanation": (
            "The X-ray suggests a fracture in the pelvic or hip region. "
            "This type of fracture often requires surgical treatment, "
            "especially in older adults. Prompt medical attention is important."
        ),
    },
    "femur": {
        "names": ["Femur fracture", "Thigh bone fracture"],
        "causes": [
            "High-energy trauma (accident)",
            "Fall from significant height",
            "Pathological fracture",
        ],
        "precautions": [
            "Emergency medical care required",
            "Surgical fixation usually necessary",
            "No weight bearing",
            "Long-term physiotherapy",
        ],
        "healing": {"Mild": "8-12 weeks", "Moderate": "12-16 weeks", "Severe": "16-24 weeks"},
        "explanation": (
            "A fracture of the femur (thigh bone) is indicated. "
            "This is a serious fracture that usually requires surgery. "
            "Full recovery typically takes several months with physiotherapy."
        ),
    },
    "limb": {
        "names": ["Limb fracture", "Long bone fracture"],
        "causes": [
            "Fall or accident",
            "Direct impact",
            "Twisting injury",
        ],
        "precautions": [
            "Immobilize the affected limb",
            "Apply ice and elevate",
            "Consult an orthopaedic doctor",
        ],
        "healing": {"Mild": "4-6 weeks", "Moderate": "6-10 weeks", "Severe": "10-16 weeks"},
        "explanation": (
            "A fracture is visible in the limb bone. "
            "Treatment depends on the exact location and type. "
            "Please see an orthopaedic specialist for the best treatment plan."
        ),
    },
}


class ExplanationGenerator:
    """Generate patient-friendly structured medical insights."""

    def generate(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        detected = detection["fracture_detected"]
        part_key = detection.get("body_part_key", "limb")
        part_label = detection.get("body_part_label", "Limb Bone")
        type_info = detection.get("fracture_type_info", {})
        confidence = detection.get("confidence", 0)

        if not detected:
            return self._no_fracture_result(part_label)

        info = FRACTURE_DB.get(part_key, FRACTURE_DB["limb"])
        severity = self._compute_severity(confidence, type_info)

        # pick a fracture name — vary by fracture pattern
        pattern = type_info.get("pattern", "linear")
        frac_type_name = type_info.get("type", "Simple fracture")

        name_idx = hash(pattern) % len(info["names"])
        fracture_name = info["names"][name_idx]

        healing = info["healing"].get(severity, "6-8 weeks")

        explanation = (
            f"{info['explanation']} "
            f"The fracture pattern appears to be a {frac_type_name.lower()}. "
            f"Based on the analysis, the severity is estimated as {severity.lower()}. "
            f"Expected healing time with proper treatment is approximately {healing}."
        )

        return {
            "fracture_name": fracture_name,
            "fracture_type": frac_type_name,
            "location": part_label,
            "possible_causes": info["causes"],
            "precautions": info["precautions"],
            "healing_time": healing,
            "severity": severity,
            "explanation_en": explanation,
        }

    # ── helpers ────────────────────────────────────────────
    @staticmethod
    def _compute_severity(confidence: float, type_info: Dict) -> str:
        pattern = type_info.get("pattern", "")
        if pattern in ("multi-fragment",) or confidence > 0.85:
            return "Severe"
        if confidence < 0.45 or pattern in ("subtle", "incomplete"):
            return "Mild"
        return "Moderate"

    @staticmethod
    def _no_fracture_result(part_label: str) -> Dict[str, Any]:
        return {
            "fracture_name": "None detected",
            "fracture_type": "N/A",
            "location": part_label,
            "possible_causes": [],
            "precautions": [
                "If pain persists, consult a doctor",
                "Consider follow-up imaging in 10-14 days",
            ],
            "healing_time": "N/A",
            "severity": "None",
            "explanation_en": (
                f"No obvious fracture was detected in the {part_label} region "
                f"on this X-ray. However, some fractures (like hairline or "
                f"stress fractures) can be difficult to see on initial X-rays. "
                f"If you continue to have pain, please see your doctor for "
                f"a follow-up examination or advanced imaging such as MRI."
            ),
        }