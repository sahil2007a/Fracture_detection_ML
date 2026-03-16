import React from "react";
import { useNavigate } from "react-router-dom";
import AnnotatedImage from "../components/AnnotatedImage";
import ResultCard from "../components/ResultCard";
import LanguageToggle from "../components/LanguageToggle";

function Results({ data }) {
  const navigate = useNavigate();
  const [lang, setLang] = React.useState("en");

  if (!data) {
    return (
      <div className="results-empty">
        <h2>No Analysis Available</h2>
        <p>Please upload an X-ray image first.</p>
        <button className="btn-primary" onClick={() => navigate("/")}>
          ← Go to Upload
        </button>
      </div>
    );
  }

  const explanation =
    lang === "hi" ? data.explanation_hi : data.explanation_en;

  return (
    <div className="results-page">
      {/* back button */}
      <button className="btn-outline back-btn" onClick={() => navigate("/")}>
        ← New Analysis
      </button>

      <h1 className="results-title">Analysis Results</h1>

      {/* language toggle */}
      <LanguageToggle lang={lang} onChange={setLang} />

      <div className="results-grid">
        {/* ── left: annotated image ───────────────── */}
        <div className="results-image-col">
          {data.annotated_image && (
            <AnnotatedImage
              src={data.annotated_image}
              originalSrc={data.original_image}
            />
          )}
          {data.processing_time_sec && (
            <p className="meta">
              Processed in {data.processing_time_sec}s
            </p>
          )}
        </div>

        {/* ── right: structured output ────────────── */}
        <div className="results-info-col">
          {/* status badge */}
          <div
            className={`status-badge ${
              data.fracture_detected ? "badge-danger" : "badge-success"
            }`}
          >
            {data.fracture_detected
              ? "⚠️ Fracture Detected"
              : "✅ No Fracture Detected"}
            {data.confidence != null && (
              <span className="conf">
                {" "}
                — Confidence: {(data.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>

          {/* cards */}
          <div className="card-grid">
            <ResultCard
              label={lang === "hi" ? "फ्रैक्चर का नाम" : "Fracture Name"}
              value={data.fracture_name}
            />
            <ResultCard
              label={lang === "hi" ? "फ्रैक्चर का प्रकार" : "Fracture Type"}
              value={data.fracture_type}
            />
            <ResultCard
              label={lang === "hi" ? "स्थान" : "Location"}
              value={data.location}
            />
            <ResultCard
              label={lang === "hi" ? "गंभीरता" : "Severity"}
              value={data.severity}
            />
            <ResultCard
              label={
                lang === "hi" ? "ठीक होने का समय" : "Healing Time"
              }
              value={data.healing_time}
            />
          </div>

          {/* causes */}
          {data.possible_causes?.length > 0 && (
            <div className="info-section">
              <h3>{lang === "hi" ? "संभावित कारण" : "Possible Causes"}</h3>
              <ul>
                {data.possible_causes.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* precautions */}
          {data.precautions?.length > 0 && (
            <div className="info-section">
              <h3>
                {lang === "hi"
                  ? "सावधानियाँ / सलाह"
                  : "Precautions"}
              </h3>
              <ul>
                {data.precautions.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>
          )}

          {/* explanation */}
          <div className="info-section explanation-box">
            <h3>
              {lang === "hi" ? "विस्तृत विवरण" : "Medical Explanation"}
            </h3>
            <p>{explanation}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Results;