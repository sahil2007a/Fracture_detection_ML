import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Upload from "../components/Upload";
import { analyzeImage, analyzeReport } from "../services/api";

function Home({ onResult }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState("image"); // "image" | "report"

  const handleUpload = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const data =
        mode === "image"
          ? await analyzeImage(file)
          : await analyzeReport(file);
      onResult(data);
      navigate("/results");
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          err.message ||
          "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      {/* Hero */}
      <section className="hero">
        <h1>
          AI-Powered <span className="highlight">X-Ray</span> Fracture
          Analysis
        </h1>
        <p className="subtitle">
          Upload an X-ray image or a scanned radiology report and let our
          AI detect fractures, highlight them visually, and generate
          patient-friendly medical insights — in English and Hindi.
        </p>
      </section>

      {/* Mode toggle */}
      <div className="mode-toggle">
        <button
          className={mode === "image" ? "active" : ""}
          onClick={() => setMode("image")}
        >
          🩻 X-Ray Image
        </button>
        <button
          className={mode === "report" ? "active" : ""}
          onClick={() => setMode("report")}
        >
          📄 Radiology Report
        </button>
      </div>

      {/* Upload */}
      <Upload onUpload={handleUpload} loading={loading} mode={mode} />

      {/* Error */}
      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Features */}
      <section className="features">
        <div className="feature-card">
          <div className="feature-icon">🔍</div>
          <h3>Fracture Detection</h3>
          <p>
            AI locates fracture regions and highlights them with bounding
            boxes and wireframe overlays.
          </p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">📋</div>
          <h3>Structured Insights</h3>
          <p>
            Get fracture type, location, causes, precautions, healing
            time, and a plain-English explanation.
          </p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🌐</div>
          <h3>Multi-Language</h3>
          <p>
            Explanations are available in English and Hindi so every
            patient can understand.
          </p>
        </div>
      </section>
    </div>
  );
}

export default Home;